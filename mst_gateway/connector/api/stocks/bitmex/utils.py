import re
from typing import Union, Optional, Tuple
from datetime import datetime
from mst_gateway.connector import api
from mst_gateway.connector.api.utils import time2timestamp
from . import var


def load_symbol_data(raw_data: dict, state_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('timestamp'))
    mark_price = to_float(raw_data.get('markPrice'))
    face_price, _reversed = calc_face_price(symbol, mark_price)
    return {
        'time': symbol_time,
        'timestamp': time2timestamp(symbol_time),
        'symbol': symbol,
        'price': to_float(raw_data.get('lastPrice')),
        'price24': to_float(raw_data.get('prevPrice24h')),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed,
        'pair': state_data.get('pair'),
        'tick': state_data.get('tick'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'symbol_schema': state_data.get('symbol_schema'),
    }


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('lastPrice'))} for c in currency]


def load_exchange_symbol_info(raw_data: list) -> list:
    symbol_list = []
    for d in raw_data:
        symbol = d.get('symbol')
        base_asset = d.get('rootSymbol')

        if re.search(r'\d{2}$', symbol):
            symbol_schema = 'futures'
        else:
            symbol_schema = 'margin1'

        symbol_list.append(
            {
                'symbol': symbol,
                'base_asset': base_asset,
                'quote_asset': _quote_asset(symbol, base_asset),
                'schema': 'margin1',
                'symbol_schema': symbol_schema,
                'tick': to_float(d.get('tickSize'))
            }
        )
    return symbol_list


def _quote_asset(symbol, base_asset):
    quote_asset = symbol[len(base_asset):]
    return quote_asset


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


def load_order_data(raw_data: dict, skip_undef=False) -> dict:
    data = {
        'order_id': raw_data.get('clOrdID'),
        'symbol': raw_data.get('symbol'),
        'value': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPx'),
        'type': raw_data.get('ordType'),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'created': to_date(raw_data.get('timestamp')),
        'active': raw_data.get('ordStatus') != "New",
        'schema': api.OrderSchema.margin1
    }
    for k in data:
        if data[k] is None and skip_undef:
            del data[k]
            continue
        if k == 'type':
            data[k] = load_order_type(data[k])
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


def load_trade_data(raw_data: dict) -> dict:
    return load_quote_data(raw_data)


def load_quote_data(raw_data: dict) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol').lower(),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
    }


def load_quote_bin_data(raw_data: dict, schema: str = None) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol'),
        'schema': schema,
        'open': to_float(raw_data.get("open")),
        'close': to_float(raw_data.get("close")),
        'high': to_float(raw_data.get("high")),
        'low': to_float(raw_data.get('low')),
        'volume': raw_data.get('volume'),
    }


def load_order_book_data(raw_data: dict) -> dict:
    return {
        'id': raw_data.get('id'),
        'symbol': raw_data.get('symbol').lower(),
        'price': to_float(raw_data.get("price")),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
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
        'volume': quote['volume']
    }


def update_quote_bin(quote_bin: dict, quote: dict) -> dict:
    quote_bin['timestamp'] = quote['timestamp']
    quote_bin['time'] = quote['time']
    quote_bin['close'] = quote['price']
    quote_bin['high'] = max(quote_bin['high'], quote['price'])
    quote_bin['low'] = min(quote_bin['low'], quote['price'])
    quote_bin['volume'] += quote['volume']
    return quote_bin


def load_wallet_data(raw_data: dict) -> dict:
    return {
        'balances': [
            {
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
        ]
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
        if b['currency'].lower() == asset.lower():
            _price = 1
        else:
            _price = currencies.get(f"{b['currency']}{asset}".lower()) or 0
        for f in fields:
            total_balance[f] += _price * (b[f] or 0)
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


def calc_face_price(symbol: str, price: float) -> Tuple[Optional[float],
                                                        Optional[bool]]:
    _symbol = symbol.lower()
    result = (None, None)
    try:
        if _symbol == "xbtusd":
            result = (1 / price, True)
        elif re.match(r'xbt[fghjkmnquvxz]\d{2}$', _symbol):
            result = (1 / price, True)
        elif _symbol in ('xbt7d_u105', 'xbt7d_d95'):
            result = (0.1 * price, False)
        elif _symbol == 'ethusd':
            result = (1e-6 * price, False)
        elif _symbol == 'xrpusd':
            result = (0.0002 * price, False)
        elif re.match(r'(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}',
                      _symbol):
            result = (price, False)
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    return result


def calc_price(symbol: str, face_price: float) -> Optional[float]:
    _symbol = symbol.lower()
    result = None
    try:
        if _symbol == "xbtusd":
            result = 1 / face_price
        elif re.match(r'xbt[fghjkmnquvxz]\d{2}$', _symbol):
            result = 1 / face_price
        elif _symbol in ('xbt7d_u105', 'xbt7d_d95'):
            result = 10 * face_price
        elif _symbol == 'ethusd':
            result = 1e+6 * face_price
        elif _symbol == 'xrpusd':
            result = face_price / 0.0002
        elif re.match(r'(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}$',
                      _symbol):
            result = face_price
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    return result


def split_order_book(ob_items, side, offset):
    result = {}
    buy_i = 0
    if side == var.BITMEX_BUY or side is None:
        result[api.BUY] = []
    if side == var.BITMEX_SELL or side is None:
        result[api.SELL] = []
    for _ob in ob_items:
        if side and _ob['side'] != side:
            continue
        data = load_order_book_data(_ob)
        if _ob['side'] == var.BITMEX_BUY:
            buy_i += 1
            if buy_i > offset:
                result[api.BUY].append(data)
        if _ob['side'] == var.BITMEX_SELL:
            result[api.SELL].append(data)
    if offset and api.SELL in result:
        result[api.SELL] = result[api.SELL][:-offset]
    return result
