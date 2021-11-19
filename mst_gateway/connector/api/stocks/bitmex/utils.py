import re
from typing import Dict, Union, Optional
from datetime import datetime, timedelta
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector import api
from mst_gateway.connector.api.utils.utils import convert_to_currency, load_wallet_summary_in_usd
from mst_gateway.exceptions import ConnectorError
from mst_gateway.connector.api.types.order import LeverageType, OrderSchema
from mst_gateway.utils import delta
from . import var
from .var import BITMEX_ORDER_STATUS_MAP
from .converter import BitmexOrderTypeConverter
from ...types.asset import to_system_asset
from ...types.binsize import BinSize
from ...utils.order_book import generate_order_book_id


def load_symbol_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('timestamp'))
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    face_price, _reversed = BitmexFinFactory.calc_face_price(symbol, price)
    data = {
        'time': symbol_time,
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': delta(price, price24),
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed,
        'volume24': raw_data.get('volume24h'),
        'mark_price': raw_data.get('markPrice'),
        'high_price': to_float(raw_data.get('highPrice')),
        'low_price': to_float(raw_data.get('lowPrice'))
    }
    if isinstance(state_data, dict):
        data.update({
            'expiration': state_data.get('expiration'),
            'expiration_date': state_data.get('expiration_date'),
            'pair': state_data.get('pair'),
            'tick': state_data.get('tick'),
            'volume_tick': state_data.get('volume_tick'),
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema'),
            'symbol_schema': state_data.get('symbol_schema'),
            'created': to_date(state_data.get('created')),
            'max_leverage': state_data.get('max_leverage')
        })
    return data


def load_symbol_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_iso_datetime(raw_data.get('timestamp'))
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    face_price, _reversed = BitmexFinFactory.calc_face_price(symbol, price)
    data = {
        'tm': symbol_time,
        's': symbol,
        'p': price,
        'p24': price24,
        'dt': delta(price, price24),
        'fp': face_price,
        'bip': to_float(raw_data.get('bidPrice')),
        'asp': to_float(raw_data.get('askPrice')),
        're': _reversed,
        'v24': raw_data.get('volume24h'),
        'mp': to_float(raw_data.get('markPrice')),
        'hip': to_float(raw_data.get("highPrice")),
        'lop': to_float(raw_data.get('lowPrice'))
    }
    if isinstance(state_data, dict):
        data.update({
            'exp': state_data.get('expiration'),
            'expd': state_data.get('expiration_date'),
            'pa': state_data.get('pair'),
            'tck': state_data.get('tick'),
            'vt': state_data.get('volume_tick'),
            'ss': state_data.get('system_symbol'),
            'ssch': state_data.get('symbol_schema'),
            'crt': to_iso_datetime(state_data.get('created')),
            'mlvr': state_data.get('max_leverage')
        })
    return data


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('lastPrice'))} for c in currency]


def load_symbols_currencies(currency: list, state_data: dict) -> dict:
    currencies = {}
    for cur in currency:
        symbol = cur.get('symbol', '').lower()
        if state_info := state_data.get(symbol):
            currencies.update({
                symbol: {
                    'pair': state_info['pair'],
                    'expiration': state_info.get('expiration'),
                    'price': to_float(cur.get('lastPrice'))
                }
            })
    return currencies


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
        max_leverage = 100 if d.get('initMargin', 0) <= 0 else 1 / d['initMargin']

        symbol_list.append(
            {
                'symbol': symbol,
                'system_symbol': system_symbol.lower(),
                'base_asset': base_asset,
                'quote_asset': quote_asset,
                'system_base_asset': system_base_asset,
                'system_quote_asset': system_quote_asset,
                'expiration': expiration,
                'expiration_date': to_date(d.get('expiry')),
                'pair': [base_asset.upper(), quote_asset.upper()],
                'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                'schema': OrderSchema.margin1,
                'symbol_schema': symbol_schema,
                'tick': tick,
                'volume_tick': volume_tick,
                'max_leverage': max_leverage
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


def load_order_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    order_time = to_date(raw_data.get('timestamp'))
    data = {
        'exchange_order_id': raw_data.get('orderID'),
        'symbol': raw_data.get('symbol'),
        'volume': to_float(raw_data.get('orderQty')),
        'filled_volume': to_float(raw_data.get('cumQty')),
        'stop': to_float(raw_data.get('stopPx')),
        'side': load_order_side(raw_data.get('side')),
        'price': to_float(raw_data.get('price')),
        'time': order_time,
        'active': bool(raw_data.get('ordStatus') != "New"),
        'type': raw_data.get('ordType', '').lower(),
        'execution': raw_data.get('ordType', '').lower(),
    }
    if isinstance(state_data, dict):
        order_type_and_exec = load_order_type_and_exec(state_data.get('schema'), raw_data.get('ordType'))
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema'),
            **order_type_and_exec,
        })
    return data


def load_order_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    data = {
        'eoid': raw_data.get('orderID'),
        'sd': load_order_side(raw_data.get('side')),
        'tv': to_float(raw_data.get('lastQty')),
        'tp': to_float(raw_data.get('lastPx')),
        'vl': to_float(raw_data.get('orderQty')),
        'p': to_float(raw_data.get('price')),
        'st': load_ws_order_status(raw_data.get('ordStatus')),
        'lv': to_float(raw_data.get('leavesQty')),
        'fv': to_float(raw_data.get('cumQty')),
        'ap': to_float(raw_data.get('avgPx')),
        's': raw_data.get('symbol'),
        'stp': to_float(raw_data.get('stopPx')),
        'tm': to_iso_datetime(raw_data.get('timestamp')),
        't': raw_data.get('ordType', '').lower(),
        'exc': raw_data.get('ordType', '').lower(),
    }
    if isinstance(state_data, dict):
        order_type_and_exec = load_order_type_and_exec(state_data.get('schema'), raw_data.get('ordType'))
        data.update({
            'ss': state_data.get('system_symbol'),
            't': order_type_and_exec.get('type'),
            'exc': order_type_and_exec.get('execution')
        })
    return data


def load_ws_order_status(bitmex_order_status: Optional[str]) -> Optional[str]:
    return var.BITMEX_ORDER_STATUS_MAP.get(bitmex_order_status) or api.OrderState.closed


def load_position_side_by_volume(volume: Optional[float]) -> Optional[int]:
    if isinstance(volume, (int, float)):
        if volume > 0:
            return api.BUY
        elif volume < 0:
            return api.SELL
    return None


def load_ws_position_action(state_volume: float, volume: float) -> str:
    if not state_volume and volume:
        return 'create'
    elif state_volume and not volume:
        return 'delete'
    elif state_volume and volume and (
            (state_volume > 0 > volume) or
            (state_volume < 0 < volume)
    ):
        return 'reverse'
    return 'update'


def load_position_ws_data(raw_data: dict, state_data: Optional[dict], exchange_rates: dict) -> dict:
    expiration = None
    state_volume = to_float(raw_data.get('state_volume'))
    volume = to_float(raw_data.get('currentQty'))
    side = load_position_side_by_volume(volume)
    unrealised_pnl = to_xbt(raw_data.get('unrealisedPnl'))
    leverage_type, leverage = load_leverage(raw_data)
    _timestamp = raw_data.get('timestamp') or datetime.now()
    data = {
        'tm': to_iso_datetime(_timestamp),
        's': raw_data.get('symbol'),
        'mp': to_float(raw_data.get('markPrice')),
        'upnl': unrealised_pnl,
        'vl': volume,
        'lp': to_float(raw_data.get('liquidationPrice')),
        'ep': to_float(raw_data.get('avgEntryPrice')),
        'sd': side if side is not None else raw_data.get('side'),
        'lvrp': leverage_type,
        'lvr': leverage,
        'act': load_ws_position_action(state_volume, volume),
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
        if exp := state_data.get('expiration', None):
            expiration = exp
    data['upnl'] = load_ws_position_unrealised_pnl(unrealised_pnl, exchange_rates, expiration)
    return data


def load_ws_position_unrealised_pnl(base: Union[float, dict], exchange_rates: dict, expiration: Optional[str]) -> dict:
    if expiration and (xbt_to_usd := exchange_rates.get(f"xbt{expiration}".lower())):
        pass
    else:
        xbt_to_usd = exchange_rates.get('xbt')
    if isinstance(base, float):
        unrealised_pnl = {
            'base': base,
            'btc': base,
            'usd': to_usd(base, xbt_to_usd)
        }
        return unrealised_pnl
    return base


def to_usd(xbt_value: float, coin_to_usd: float) -> Optional[float]:
    try:
        return xbt_value * coin_to_usd
    except TypeError:
        return None


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('id')).lower()
    }
    return data


def load_api_key_permissions(raw_data: dict, api_key: str, schemas: iter) -> dict:
    for acc in raw_data:
        if acc.get('id') == api_key:
            if 'order' in acc.get('permissions'):
                return {schema: (True if schema == OrderSchema.margin1 else False) for schema in schemas}
            else:
                return {schema: False for schema in schemas}
    return {schema: False for schema in schemas}


def load_trade_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    return load_quote_data(raw_data, state_data)


def load_quote_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    data = {
        'time': quote_time,
        'symbol': raw_data.get('symbol'),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side')),
    }
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_ws_quote_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_time = to_iso_datetime(raw_data.get('timestamp'))
    data = {
        'tm': quote_time,
        's': raw_data.get('symbol'),
        'p': to_float(raw_data.get('price')),
        'vl': raw_data.get('size'),
        'sd': load_order_side(raw_data.get('side')),
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_quote_bin_data(raw_data: dict, state_data: Optional[dict], binsize=None) -> dict:
    if binsize and isinstance(raw_data.get('timestamp'), datetime):
        raw_data['timestamp'] = raw_data['timestamp'] - binsize2timedelta(binsize)
    quote_bin_time = to_date(raw_data.get('timestamp'))
    data = {
        'time': quote_bin_time,
        'symbol': raw_data.get('symbol'),
        'open_price': to_float(raw_data.get('open')),
        'close_price': to_float(raw_data.get('close')),
        'high_price': to_float(raw_data.get('high')),
        'low_price': to_float(raw_data.get('low')),
        'volume': raw_data.get('volume')
    }
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_ws_quote_bin_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_bin_time = to_iso_datetime(raw_data.get('timestamp'))
    data = {
        'tm': quote_bin_time,
        's': raw_data.get('symbol'),
        'opp': to_float(raw_data.get('open')),
        'clp': to_float(raw_data.get('close')),
        'hip': to_float(raw_data.get('high')),
        'lop': to_float(raw_data.get('low')),
        'vl': raw_data.get('volume')
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def binsize2timedelta(binsize):
    return timedelta(seconds=BinSize(binsize).to_sec)


def load_order_book_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    symbol = raw_data.get('symbol')
    price = to_float(raw_data.get('price'))
    _id = generate_order_book_id(symbol, price, state_data)
    data = {
        'id': _id,
        'symbol': symbol,
        'price': price,
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
    }
    if isinstance(state_data, dict):
        data.update({
            'schema': state_data.get('schema'),
            'system_symbol': state_data.get('system_symbol')
        })
    return data


def load_ws_order_book_data(raw_data: dict, state_data: Optional[dict], price_by_id: dict) -> dict:
    _id = raw_data.get('id')
    symbol = raw_data.get('symbol')
    price = to_float(raw_data.get('price') or to_float(price_by_id[symbol].get(_id)))
    _id = generate_order_book_id(symbol, price, state_data)
    data = {
        'id': _id,
        's': raw_data.get('symbol'),
        'p': price,
        'vl': raw_data.get('size'),
        'sd': load_order_side(raw_data.get('side'))
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def quote2bin(quote: dict) -> dict:
    return {
        's': quote['s'],
        'tm': quote['tm'],
        'opp': quote['p'],
        'clp': quote['p'],
        'hip': quote['p'],
        'lop': quote['p'],
        'vl': quote['vl'],
        'ss': quote.get('ss')
    }


def update_quote_bin(quote_bin: dict, quote: dict) -> dict:
    quote_bin['tm'] = quote['tm']
    quote_bin['clp'] = quote['p']
    quote_bin['hip'] = max(quote_bin['hip'], quote['p'])
    quote_bin['lop'] = min(quote_bin['lop'], quote['p'])
    quote_bin['vl'] += quote['vl']
    quote_bin['ss'] = quote.get('ss')
    return quote_bin


def load_wallet_data(raw_data: dict, currencies: dict, assets: Union[tuple, list], fields: tuple,
                     is_for_ws=False) -> dict:
    if is_for_ws:
        bls_key = 'bls'
        balances = [load_ws_wallet_detail_data(raw_data)]
    else:
        bls_key = 'balances'
        balances = [load_wallet_detail_data(raw_data)]

    balances_summary = {}
    total_balance = {OrderSchema.margin1: {}}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields, is_for_ws=is_for_ws)
    for asset in assets:
        total_balance[OrderSchema.margin1][asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset))
        )
    load_total_wallet_summary(balances_summary, total_balance, assets, fields, is_for_ws=is_for_ws)
    return {
        bls_key: balances,
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


def load_ws_wallet_detail_data(raw_data: dict, asset: str = None) -> dict:
    if asset and asset.lower() != raw_data.get('currency', '').lower():
        raise ConnectorError(f"Invalid asset {asset}.")
    return {
        'cur': raw_data.get('currency', '').upper(),
        'bl': to_xbt(raw_data.get('walletBalance')),
        'wbl': to_xbt(raw_data.get('withdrawableMargin')),
        'upnl': to_xbt(raw_data.get('unrealisedPnl')),
        'mbl': to_xbt(raw_data.get('marginBalance')),
        'mm': to_xbt(raw_data.get('maintMargin')),
        'im': to_xbt(raw_data.get('initMargin')),
        'am': to_xbt(raw_data.get('availableMargin')),
        't': to_wallet_state_type(to_xbt(raw_data.get('maintMargin')))
    }


def load_wallet_asset_balance(raw_data: dict) -> dict:
    data = {
        raw_data.get('currency', '').lower(): to_xbt(raw_data.get('walletBalance')),
    }
    return data


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def to_exchange_asset(asset: str):
    if asset == 'btc':
        return 'xbt'
    return asset


def load_total_wallet_summary(total_summary: dict, total_balance: dict, assets: Union[list, tuple],
                              fields: Union[list, tuple], is_for_ws=False):
    for schema in total_balance.keys():
        for field in fields:
            t_field = f't{field}' if is_for_ws else f'total_{field}'
            total_summary.setdefault(t_field, {})
            for asset in assets:
                total_summary[t_field].setdefault(asset, 0)
                total_summary[t_field][asset] += total_balance[schema][asset][field]
    return total_summary


def load_commissions(commissions: dict) -> list:
    commissions_list = []
    for symbol, commission in commissions.items():
        for vip in var.BITMEX_VIP_LEVELS:
            commissions_list.append(
                {
                    'symbol': symbol.lower(),
                    'maker': to_float(commission['makerFee']),
                    'taker': to_float(vip['taker']),
                    'type': vip['type'],
                }
            )
    return commissions_list


def load_vip_level(trading_volume: Union[str, float]) -> str:
    trading_volume = to_float(trading_volume)
    if trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP4']:
        vip_level = '4'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP3']:
        vip_level = '3'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP2']:
        vip_level = '2'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP1']:
        vip_level = '1'
    else:
        vip_level = '0'
    return vip_level


def to_xbt(value: int):
    if isinstance(value, int):
        return round(value / 10 ** 8, 8)
    return value


def to_date(token: Union[datetime, str]) -> Optional[datetime]:
    if not token:
        return None
    if isinstance(token, datetime):
        return token
    try:
        return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT)
    except (ValueError, TypeError, IndexError):
        return None


def to_iso_datetime(token: Union[datetime, str]) -> Optional[str]:
    if not token:
        return None
    try:
        if isinstance(token, datetime):
            return token.strftime(api.DATETIME_FORMAT)
        elif isinstance(token, str):
            return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT).strftime(api.DATETIME_FORMAT)
    except (ValueError, TypeError, IndexError):
        return None


def to_float(token: Union[int, float, str, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None


def symbol2stock(symbol):
    return symbol.upper() if symbol is not None else None


def stock2symbol(symbol):
    return symbol.lower() if symbol is not None else None


def split_order_book(ob_items, state_data: Optional[dict]):
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
        new_options['ttl'] = var.PARAMETER_NAMES_MAP.get(options.get('ttl'))
    if options.get('is_iceberg'):
        new_options['iceberg_volume'] = options['iceberg_volume'] or 0

    if options.get('is_passive'):
        new_options['is_passive'] = 'ParticipateDoNotInitiate'
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


def load_leverage(raw_data: dict) -> tuple:
    if raw_data.get('crossMargin'):
        return LeverageType.cross, to_float(raw_data.get('leverage'))
    else:
        return LeverageType.isolated, to_float(raw_data.get('leverage'))


def store_leverage(leverage_type: str, leverage: float) -> float:
    if leverage_type == LeverageType.cross:
        return var.BITMEX_CROSS_LEVERAGE_TYPE_PARAM
    return leverage or 0


def load_position(raw_data: dict, schema: str) -> dict:
    return {
        'schema': schema,
        'symbol': raw_data.get('symbol'),
        'side': load_position_side_by_volume(to_float(raw_data.get('currentQty'))),
        'volume': to_float(raw_data.get('currentQty')),
        'entry_price': to_float(raw_data.get('avgEntryPrice')),
        'mark_price': to_float(raw_data.get('markPrice')),
        'unrealised_pnl': to_xbt(raw_data.get('unrealisedPnl')),
        'leverage_type': load_leverage(raw_data)[0],
        'leverage': to_float(raw_data.get('leverage')),
        'liquidation_price': to_float(raw_data.get('liquidationPrice')),
        }


def load_positions_list(raw_data: list, schema: str) -> list:
    return [load_position(data, schema) for data in raw_data if to_float(data.get('currentQty')) != 0]
