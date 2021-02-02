import re
from typing import Dict, Union, Optional
from datetime import datetime, timedelta, timezone
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector import api
from mst_gateway.connector.api.utils import time2timestamp
from mst_gateway.exceptions import ConnectorError
from mst_gateway.connector.api.types.order import OrderSchema
from mst_gateway.utils import delta
from . import var
from .var import BITMEX_ORDER_STATUS_MAP
from .converter import BitmexOrderTypeConverter
from ...types.asset import to_system_asset
from ...types.binsize import BinSize
from ...types.order import LeverageType


def load_symbol_data(raw_data: dict, state_data: dict, is_iso_datetime=False) -> dict:
    symbol = raw_data.get('symbol')
    symbol_datetime = to_date(raw_data.get('timestamp'))
    symbol_time = to_iso_datetime(symbol_datetime) if is_iso_datetime else symbol_datetime
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    face_price, _reversed = BitmexFinFactory.calc_face_price(symbol, price)
    return {
        'time': symbol_time,
        'timestamp': time2timestamp(symbol_datetime),
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': delta(price, price24),
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed,
        'volume24': raw_data.get('volume24h'),
        'expiration': state_data.get('expiration'),
        'pair': state_data.get('pair'),
        'tick': state_data.get('tick'),
        'volume_tick': state_data.get('volume_tick'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'symbol_schema': state_data.get('symbol_schema'),
        'created': to_iso_datetime(state_data.get('created')) if is_iso_datetime else state_data.get('created'),
    }


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('lastPrice'))} for c in currency]


def load_symbols_currencies(currency: list) -> dict:
    return {c.get('symbol', '').lower(): to_float(c.get('lastPrice')) for c in currency}


def load_funding_rates(funding_rates: list) -> list:
    return [
        {
            'symbol': funding_rate['symbol'].lower(),
            'funding_rate': to_float(funding_rate['fundingRate']),
            'time': to_date(funding_rate['timestamp']),
        } for funding_rate in funding_rates
    ]


def load_exchange_symbol_info(raw_data: list) -> list:
    symbol_list = []
    for d in raw_data:
        symbol = d.get('symbol')
        base_asset = d.get('underlying')
        quote_currency = d.get('quoteCurrency')

        if re.search(r'\d{2}$', symbol):
            symbol_schema = OrderSchema.futures
        else:
            symbol_schema = OrderSchema.margin1

        quote_asset, expiration = _quote_asset(symbol, base_asset, quote_currency, symbol_schema)
        system_base_asset = to_system_asset(base_asset)
        if expiration:
            system_quote_asset = expiration
            expiration = expiration[-3:]
        else:
            system_quote_asset = to_system_asset(quote_asset)
        system_symbol = f"{system_base_asset}{system_quote_asset}"

        tick = to_float(d.get('tickSize'))
        volume_tick = to_float(d.get('lotSize'))

        symbol_list.append(
            {
                'symbol': symbol,
                'system_symbol': system_symbol.lower(),
                'base_asset': base_asset,
                'quote_asset': quote_asset,
                'system_base_asset': system_base_asset,
                'system_quote_asset': system_quote_asset,
                'expiration': expiration,
                'pair': [base_asset.upper(), quote_asset.upper()],
                'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                'schema': OrderSchema.margin1,
                'symbol_schema': symbol_schema,
                'tick': tick,
                'volume_tick': volume_tick,
            }
        )
    return symbol_list


def _quote_asset(symbol, base_asset, quote_currency, symbol_schema):
    quote_asset = symbol[len(base_asset):].upper()
    if symbol_schema == OrderSchema.futures:
        return quote_currency, quote_asset
    return quote_asset, None


def store_order_type(order_type: str) -> str:
    converter = BitmexOrderTypeConverter
    return converter.store_type(order_type)


def load_order_type_and_exec(schema: str, exchange_order_type: str) -> dict:
    converter = BitmexOrderTypeConverter
    return converter.load_type_and_exec(schema, exchange_order_type)


def store_order_side(order_side: int) -> Optional[str]:
    if order_side is None:
        return None
    if order_side == api.SELL:
        return var.BITMEX_SELL
    return var.BITMEX_BUY


def load_order_side(order_side: str) -> int:
    if order_side.lower() == var.BITMEX_SELL.lower():
        return api.SELL
    return api.BUY


def load_order_data(raw_data: dict, state_data: dict, skip_undef=False) -> dict:
    order_type_and_exec = load_order_type_and_exec(state_data.get('schema'),
                                                   raw_data.get('ordType'))
    order_time = to_date(raw_data.get('timestamp'))
    data = {
        'order_id': raw_data.get('clOrdID'),
        'exchange_order_id': raw_data.get('orderID'),
        'symbol': raw_data.get('symbol'),
        'volume': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPx'),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'time': order_time,
        'timestamp': time2timestamp(order_time),
        'active': raw_data.get('ordStatus') != "New",
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        **order_type_and_exec,
    }
    for k in data:
        if data[k] is None and skip_undef:
            del data[k]
            continue
        elif k == 'side':
            data[k] = load_order_side(data[k])
        elif k == 'active':
            data[k] = bool(data[k] != 'New')
    return data


def load_order_ws_data(raw_data: dict, state_data: dict) -> dict:
    order_type_and_exec = load_order_type_and_exec(state_data.get('schema'),
                                                   raw_data.get('ordType'))
    return {
        'order_id': raw_data.get('clOrdID'),
        'exchange_order_id': raw_data.get('orderID'),
        'side': load_order_side(raw_data.get('side')),
        'tick_volume': raw_data.get('lastQty'),
        'tick_price': raw_data.get('lastPx'),
        'volume': raw_data.get('orderQty'),
        'price': to_float(raw_data.get('price')),
        'status': BITMEX_ORDER_STATUS_MAP.get(raw_data.get('ordStatus')),
        'leaves_volume': raw_data.get('leavesQty'),
        'filled_volume': raw_data.get('cumQty'),
        'avg_price': raw_data.get('avgPx'),
        'timestamp': time2timestamp(raw_data.get('timestamp')),
        'symbol': raw_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'stop': raw_data.get('stopPx'),
        'time': to_iso_datetime(raw_data.get('timestamp')),
        **order_type_and_exec,
    }


def load_position_ws_data(raw_data: dict, state_data: dict) -> dict:
    data = {
        'time': to_iso_datetime(raw_data.get('timestamp')),
        'timestamp': time2timestamp(raw_data.get('timestamp')),
        'symbol': raw_data.get('symbol'),
        'mark_price': raw_data.get('markPrice'),
        'volume': raw_data.get('currentQty'),
        'liquidation_price': raw_data.get('liquidationPrice'),
        'entry_price': raw_data.get('avgEntryPrice'),
        'unrealised_pnl': raw_data.get('unrealisedPnl'),
        'leverage': to_float(raw_data.get('leverage')),
        'schema': state_data.get('schema'),
        'system_symbol': state_data.get('system_symbol')
    }
    if raw_data.get('crossMargin') is None:
        data['leverage_type'] = raw_data.get('leverage_type')
    else:
        data['leverage_type'] = LeverageType.cross if raw_data.get('crossMargin') else LeverageType.isolated
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('id')).lower()
    }
    return data


def load_trade_data(raw_data: dict, state_data: dict, is_iso_datetime=False) -> dict:
    return load_quote_data(raw_data, state_data, is_iso_datetime=is_iso_datetime)


def load_quote_data(raw_data: dict, state_data: dict, is_iso_datetime=False) -> dict:
    quote_time = to_iso_datetime(raw_data.get('timestamp')) if is_iso_datetime else to_date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(to_date(raw_data.get('timestamp'))),
        'symbol': raw_data.get('symbol'),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side')),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema')
    }


def load_quote_bin_data(raw_data: dict, state_data: dict, is_iso_datetime=False, binsize=None) -> dict:
    if binsize and isinstance(raw_data.get('timestamp'), datetime):
        raw_data['timestamp'] = raw_data['timestamp'] - binsize2timedelta(binsize)
    _timestamp = to_date(raw_data.get('timestamp'))
    quote_time = to_iso_datetime(_timestamp) if is_iso_datetime else _timestamp
    return {
        'time': quote_time,
        'timestamp': time2timestamp(_timestamp),
        'symbol': raw_data.get('symbol'),
        'open': to_float(raw_data.get("open")),
        'close': to_float(raw_data.get("close")),
        'high': to_float(raw_data.get("high")),
        'low': to_float(raw_data.get('low')),
        'volume': raw_data.get('volume'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema')
    }


def binsize2timedelta(binsize):
    return timedelta(seconds=BinSize(binsize).to_sec)


def load_order_book_data(raw_data: dict, state_data: dict) -> dict:
    return {
        'id': raw_data.get('id'),
        'symbol': raw_data.get('symbol'),
        'price': to_float(raw_data.get("price")),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side')),
        'schema': state_data.get('schema'),
        'system_symbol': state_data.get('system_symbol'),
    }


def quote2bin(quote: dict) -> dict:
    return {
        'symbol': quote['symbol'],
        'timestamp': quote['timestamp'],
        'time': quote['time'],
        'open': quote['price'],
        'close': quote['price'],
        'high': quote['price'],
        'low': quote['price'],
        'volume': quote['volume'],
        'system_symbol': quote.get('system_symbol'),
        'schema': quote.get('schema')
    }


def update_quote_bin(quote_bin: dict, quote: dict) -> dict:
    quote_bin['timestamp'] = quote['timestamp']
    quote_bin['time'] = quote['time']
    quote_bin['close'] = quote['price']
    quote_bin['high'] = max(quote_bin['high'], quote['price'])
    quote_bin['low'] = min(quote_bin['low'], quote['price'])
    quote_bin['volume'] += quote['volume']
    quote_bin['system_symbol'] = quote['system_symbol']
    quote_bin['schema'] = quote['schema']
    return quote_bin


def load_wallet_data(
    raw_data: dict, currencies: dict, assets: Union[tuple, list], fields: tuple
) -> dict:
    balances = [load_wallet_detail_data(raw_data)]
    balances_summary = {}
    total_balance = {OrderSchema.margin1: {}}
    for asset in assets:
        total_balance[OrderSchema.margin1][asset] = load_wallet_summary(
            currencies, balances, asset, fields
        )
    load_total_wallet_summary(balances_summary, total_balance, assets, fields)
    return {
        'balances': balances,
        **balances_summary,
    }


def load_wallet_detail_data(raw_data: dict, asset: str = None) -> dict:
    if asset and asset.lower() != raw_data.get('currency', '').lower():
        raise ConnectorError(f"Invalid asset {asset}.")
    return {
        'currency': raw_data.get('currency', '').upper(),
        'balance': to_xbt(raw_data.get('walletBalance')),
        'withdraw_balance': to_xbt(raw_data.get('withdrawableMargin')),
        'unrealised_pnl': to_xbt(raw_data.get('unrealisedPnl')),
        'margin_balance': to_xbt(raw_data.get('marginBalance')),
        'maint_margin': to_xbt(raw_data.get('maintMargin')),
        'init_margin': to_xbt(raw_data.get('initMargin')),
        'available_margin': to_xbt(raw_data.get('availableMargin')),
        'type': to_wallet_state_type(to_xbt(raw_data.get('maintMargin')))
    }


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def load_wallet_summary(currencies: dict, balances: list, asset: str,
                        fields: Union[list, tuple, None]):
    if fields is None:
        fields = ('balance',)
    if asset.lower() == 'btc':
        asset = 'xbt'
    total_balance = dict()
    for f in fields:
        total_balance[f] = 0
    for b in balances:
        if b['currency'].lower() == asset.lower() or b['currency'].lower() == 'usd':
            _price = 1
            _asset_price = 1
        else:
            _price = currencies.get(f"{b['currency']}usd".lower()) or 0
            _asset_price = currencies.get(f"{asset}usd".lower()) or 1
        for f in fields:
            total_balance[f] += _price * (b[f] or 0) / _asset_price
    return total_balance


def load_total_wallet_summary(
    total_summary: dict, total_balance: dict, assets: Union[list, tuple], fields: Union[list, tuple]
):
    for schema in total_balance.keys():
        for field in fields:
            t_field = f'total_{field}'
            total_summary.setdefault(t_field, {})
            for asset in assets:
                total_summary[t_field].setdefault(asset, 0)
                total_summary[t_field][asset] += total_balance[schema][asset][field]
    return total_summary


def load_currency(currency: dict):
    return {currency['symbol'].lower(): to_float(currency['price'])}


def load_currencies_as_dict(currencies: list):
    return {cur['symbol'].lower(): to_float(cur['price']) for cur in currencies}


def load_commissions(commissions: dict) -> list:
    return [
        {
            'symbol': symbol.lower(),
            'maker': to_float(commission['makerFee']),
            'taker': to_float(commission['takerFee']),
            'type': 'VIP0',
        } for symbol, commission in commissions.items()
    ]


def to_xbt(value: int):
    if isinstance(value, int):
        return round(value / 10 ** 8, 8)
    return value


def to_date(token: Union[datetime, str]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.strptime(token, api.DATETIME_FORMAT)
    except (ValueError, TypeError):
        return None


def to_iso_datetime(token: Union[datetime, int, str]) -> Optional[str]:
    if isinstance(token, str):
        try:
            return datetime.strptime(token, api.DATETIME_FORMAT).strftime(api.DATETIME_OUT_FORMAT)
        except ValueError:
            return None
    if isinstance(token, datetime):
        return token.strftime(api.DATETIME_OUT_FORMAT)
    if isinstance(token, int):
        return datetime.fromtimestamp(token, tz=timezone.utc).strftime(api.DATETIME_OUT_FORMAT)
    return None


def to_float(token: Union[int, float, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None


def symbol2stock(symbol):
    return symbol.upper() if symbol is not None else None


def stock2symbol(symbol):
    return symbol.lower() if symbol is not None else None


def split_order_book(ob_items, state_data: dict):
    result = {api.BUY: [], api.SELL: []}
    for _ob in ob_items:
        data = load_order_book_data(_ob, state_data)
        if _ob['side'] == var.BITMEX_BUY:
            result[api.BUY].append(data)
        elif _ob['side'] == var.BITMEX_SELL:
            result[api.SELL].append(data)
    return result


def filter_order_book(
    splitted_ob: Dict[int, list],
    min_volume_buy: float = None,
    min_volume_sell: float = None,
) -> Dict[int, list]:
    filtered_ob = splitted_ob
    if min_volume_buy is not None and min_volume_sell is not None:
        filtered_ob[api.BUY] = [
            buy_ob for buy_ob in filtered_ob[api.BUY]
            if buy_ob.get('volume') >= min_volume_buy
        ]
        filtered_ob[api.SELL] = [
            sell_ob for sell_ob in filtered_ob[api.SELL]
            if sell_ob.get('volume') >= min_volume_sell
        ]
    elif min_volume_buy is not None:
        filtered_ob[api.BUY] = [
            buy_ob for buy_ob in filtered_ob[api.BUY]
            if buy_ob.get('volume') >= min_volume_buy
        ]
    elif min_volume_sell is not None:
        filtered_ob[api.SELL] = [
            sell_ob for sell_ob in filtered_ob[api.SELL]
            if sell_ob.get('volume') >= min_volume_sell
        ]
    return filtered_ob


def slice_order_book(splitted_ob: Dict[int, list], depth: int, offset: int) -> Dict[int, list]:
    if offset and depth:
        return {
            api.BUY: splitted_ob[api.BUY][offset:depth + offset],
            api.SELL: splitted_ob[api.SELL][-offset-depth:-offset]
        }
    elif depth:
        return {
            api.BUY: splitted_ob[api.BUY][:depth],
            api.SELL: splitted_ob[api.SELL][-depth:]
        }
    elif offset:
        return {
            api.BUY: splitted_ob[api.BUY][offset:],
            api.SELL: splitted_ob[api.SELL][:-offset]
        }
    return splitted_ob


def store_order_mapping_parameters(exchange_order_type: str) -> list:
    data = var.PARAMETERS_BY_ORDER_TYPE_MAP.get(exchange_order_type)
    if data:
        return data['params']
    return var.PARAMETERS_BY_ORDER_TYPE_MAP['Limit']['params']


def store_order_additional_parameters(exchange_order_type: str) -> dict:
    data = var.PARAMETERS_BY_ORDER_TYPE_MAP.get(exchange_order_type)
    if data:
        return data['additional_params']
    return var.PARAMETERS_BY_ORDER_TYPE_MAP['Limit']['additional_params']


def generate_parameters_by_order_type(main_params: dict, options: dict) -> dict:
    """
    Fetches specific order parameters based on the order_type value and adds them
    to the main parameters.

    """
    order_type = main_params.pop('order_type', None)
    exchange_order_type = store_order_type(order_type)
    mapping_parameters = store_order_mapping_parameters(exchange_order_type)
    options = assign_custom_parameter_values(options)
    all_params = map_api_parameter_names(
        {'order_type': exchange_order_type, **main_params, **options}
    )
    new_params = dict()
    for param_name in mapping_parameters:
        value = all_params.get(param_name)
        if value:
            new_params[param_name] = value
    new_params.update(
        store_order_additional_parameters(exchange_order_type)
    )
    return new_params


def assign_custom_parameter_values(options: Optional[dict]) -> dict:
    """
    Changes the value of certain parameters according to Binance's specification.

    """
    new_options = dict()
    if options is None:
        return new_options
    if options.get('comments'):
        new_options['text'] = options['comments']
    if options.get('ttl'):
        new_options['timeInForce'] = 'GoodTillCancel'
    if options.get('is_passive'):
        new_options['execInst'] = 'ParticipateDoNotInitiate'
    if options.get('is_iceberg'):
        new_options['displayQty'] = options['iceberg_volume'] or 0
    return new_options


def map_api_parameter_names(params: dict) -> Optional[dict]:
    """
    Changes the name (key) of any parameters that have a different name in the Bitmex API.
    Example: 'ttl' becomes 'timeInForce'

    """
    tmp_params = dict()
    for param, value in params.items():
        if value is None:
            continue
        _param = var.PARAMETER_NAMES_MAP.get(param) or param
        tmp_params[_param] = value
    return tmp_params
