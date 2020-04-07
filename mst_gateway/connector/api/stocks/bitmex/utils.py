import urllib
import json
import hmac
import hashlib
import re
from typing import Union, Optional, Tuple
from datetime import datetime
from mst_gateway.connector import api
from mst_gateway.connector.api.utils import time2timestamp
from . import var


# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + nonce + data), hex encoded.
# Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
# and the data, if present, must be JSON without whitespace between keys.
def bitmex_signature(api_secret, verb, url, nonce, postdict=None):
    """Given an API secret key and data, create a BitMEX-compatible signature."""
    data = ''
    if postdict:
        # separators remove spaces from json
        # BitMEX expects signatures from JSON built without spaces
        data = json.dumps(postdict, separators=(',', ':'))
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    if parsed_url.query:
        path = path + '?' + parsed_url.query
    message = (verb + path + str(nonce) + data).encode('utf-8')
    signature = hmac.new(api_secret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
    return signature


def load_symbol_data(raw_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = _date(raw_data.get('timestamp'))
    mark_price = _float(raw_data.get('markPrice'))
    face_price, _reversed = calc_face_price(symbol, mark_price)
    return {
        'time': symbol_time,
        'timestamp': time2timestamp(symbol_time),
        'symbol': symbol,
        'price': _float(raw_data.get('lastPrice')),
        'price24': _float(raw_data.get('prevPrice24h')),
        'pair': _get_symbol_pair(raw_data.get('symbol'),
                                 raw_data.get('rootSymbol')),
        'tick': _float(raw_data.get('tickSize')),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': _float(raw_data.get('bidPrice')),
        'ask_price': _float(raw_data.get('askPrice')),
        'reversed': _reversed
    }


def store_order_type(order_type: str) -> str:
    return var.ORDER_TYPE_WRITE_MAP.get(order_type)


def load_order_type(order_type: str) -> str:
    return var.ORDER_TYPE_READ_MAP.get(order_type)


def store_order_side(order_side: int) -> str:
    if order_side == api.SELL:
        return 'Sell'
    return 'Buy'


def load_order_side(order_side: str) -> int:
    if order_side.lower() == 'sell':
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
        'price': _float(raw_data.get('price')),
        'created': _date(raw_data.get('timestamp')),
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


def load_trade_data(raw_data: dict) -> dict:
    return load_quote_data(raw_data)


def load_quote_data(raw_data: dict) -> dict:
    quote_time = _date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol'),
        'price': _float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
    }


def load_quote_bin_data(raw_data: dict) -> dict:
    quote_time = _date(raw_data.get('timestamp'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': raw_data.get('symbol'),
        'open': _float(raw_data.get("open")),
        'close': _float(raw_data.get("close")),
        'high': _float(raw_data.get("high")),
        'low': _float(raw_data.get('low')),
        'volume': raw_data.get('volume'),
    }


def load_order_book_data(raw_data: dict) -> dict:
    return {
        'id': raw_data.get('id'),
        'symbol': raw_data.get('symbol'),
        'price': _float(raw_data.get("price")),
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


def _date(token: Union[datetime, str]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.strptime(token, api.DATETIME_FORMAT)
    except ValueError:
        return None


def _float(token: Union[int, float, None]) -> Optional[float]:
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


def _get_symbol_pair(symbol: str, root_symbol: str) -> list:
    # pylint: disable=unused-argument,fixme
    return [symbol[:3], symbol[3:]]
    # TODO: For wss packets
    # if not root_symbol:
    #     return ["", symbol]
    # try:
    #     pos = symbol.index(root_symbol)
    # except ValueError:
    #     return ["", symbol]
    # if pos > 0:
    #     return ["", symbol]
    # return [root_symbol, symbol[pos:]]
