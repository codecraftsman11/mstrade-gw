import re
from typing import Dict, Union, Optional
from datetime import datetime
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector import api
from mst_gateway.connector.api.utils import time2timestamp
from mst_gateway.exceptions import ConnectorError
from mst_gateway.connector.api.types.order import OrderSchema
from . import var


def load_symbol_data(raw_data: dict, state_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('timestamp'))
    mark_price = to_float(raw_data.get('markPrice'))
    face_price, _reversed = BitmexFinFactory.calc_face_price(symbol, mark_price)
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    return {
        'time': symbol_time,
        'timestamp': time2timestamp(symbol_time),
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': symbol_delta(price, price24),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed,
        'volume24': to_float(raw_data.get('volume24h')),
        'expiration': state_data.get('expiration'),
        'pair': state_data.get('pair'),
        'tick': state_data.get('tick'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'symbol_schema': state_data.get('symbol_schema'),
    }


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('lastPrice'))} for c in currency]


def load_symbols_currencies(currency: list) -> dict:
    return {c.get('symbol', '').lower(): to_float(c.get('lastPrice')) for c in currency}


def load_funding_rates(funding_rates: list) -> dict:
    result = dict()
    for fr in funding_rates:
        symbol = fr.get('symbol', '').lower()
        if symbol not in result.keys():
            result[symbol] = {
                'symbol': symbol, 'funding_rate': to_float(fr.get('fundingRate'))
            }
    return result


def load_exchange_symbol_info(raw_data: list) -> list:
    symbol_list = []
    for d in raw_data:
        symbol = d.get('symbol')
        base_asset = d.get('rootSymbol')
        quote_currency = d.get('quoteCurrency')

        if re.search(r'\d{2}$', symbol):
            symbol_schema = OrderSchema.futures
        else:
            symbol_schema = OrderSchema.margin1

        quote_asset, expiration = _quote_asset(symbol, base_asset, quote_currency, symbol_schema)
        symbol_list.append(
            {
                'symbol': symbol,
                'base_asset': base_asset,
                'quote_asset': quote_asset,
                'expiration': expiration,
                'pair': [base_asset.upper(), quote_asset.upper()],
                'schema': OrderSchema.margin1,
                'symbol_schema': symbol_schema,
                'tick': to_float(d.get('tickSize'))
            }
        )
    return symbol_list


def _quote_asset(symbol, base_asset, quote_currency, symbol_schema):
    quote_asset = symbol[len(base_asset):].upper()
    if symbol_schema == OrderSchema.futures:
        return quote_currency, quote_asset
    return quote_asset, None


def store_order_type(order_type: str) -> str:
    return var.ORDER_TYPE_WRITE_MAP.get(order_type)


def load_order_type(order_type: str) -> str:
    return var.ORDER_TYPE_READ_MAP.get(order_type)


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
    order_type_and_exec = var.ORDER_TYPE_AND_EXECUTION_READ_MAP.get(
        raw_data.get('ordType')
    ) or {'type': None, 'execution': None}
    data = {
        'order_id': raw_data.get('clOrdID'),
        'symbol': raw_data.get('symbol'),
        'value': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPx'),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'created': to_date(raw_data.get('timestamp')),
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


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('id')).lower()
    }
    return data


def load_trade_data(raw_data: dict, state_data: dict) -> dict:
    return load_quote_data(raw_data, state_data)


def load_quote_data(raw_data: dict, state_data: dict) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol'),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side')),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema')
    }


def load_quote_bin_data(raw_data: dict, state_data: dict) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol'),
        'open': to_float(raw_data.get("open")),
        'close': to_float(raw_data.get("close")),
        'high': to_float(raw_data.get("high")),
        'low': to_float(raw_data.get('low')),
        'volume': raw_data.get('volume'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema')
    }


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


def load_wallet_data(raw_data: dict) -> dict:
    return {
        'balances': [
            load_wallet_detail_data(raw_data)
        ]
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


def load_total_wallet_summary(total: dict, summary: dict, assets: Union[list, tuple], fields: Union[list, tuple]):
    for schema in summary.keys():
        for field in fields:
            t_field = f'total_{field}'
            if total.get(t_field) is None:
                total[t_field] = dict()
            for asset in assets:
                if total[t_field].get(asset) is None:
                    total[t_field][asset] = summary[schema][asset][field]
                else:
                    total[t_field][asset] += summary[schema][asset][field]
    return total


def load_currency(currency: dict):
    return {currency['symbol'].lower(): to_float(currency['price'])}


def load_currencies_as_dict(currencies: list):
    return {cur['symbol'].lower(): to_float(cur['price']) for cur in currencies}


def load_commission(commissions: dict, currency: str, symbol: str) -> dict:
    symbol_commission = commissions.pop(symbol.upper(), dict())
    maker = to_float(symbol_commission.get('makerFee'))
    taker = to_float(symbol_commission.get('takerFee'))
    return dict(
        currency=currency.lower(),
        maker=abs(maker) if maker is not None else None,
        taker=abs(taker) if taker is not None else None,
        type=None
    )


def to_xbt(value: int):
    if isinstance(value, int):
        return round(value / 10 ** 8, 8)
    return value


def symbol_delta(price, price24):
    if price and price24:
        return round((price - price24) / price24 * 100, 2)
    return 100


def to_date(token: Union[datetime, str]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.strptime(token, api.DATETIME_FORMAT)
    except ValueError:
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
