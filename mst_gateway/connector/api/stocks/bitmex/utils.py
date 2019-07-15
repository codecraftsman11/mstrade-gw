import urllib
import json
import hmac
import hashlib
from . import var
from .... import api


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
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'price': float(raw_data.get('lastPrice')),
    }


def store_order_type(order_type: int) -> str:
    return var.ORDER_TYPE_WRITE_MAP.get(order_type)


def load_order_type(order_type: str) -> int:
    return var.ORDER_TYPE_READ_MAP.get(order_type)


def store_order_side(order_side: int) -> str:
    if order_side == api.SELL:
        return 'Sell'
    return 'Buy'


def load_order_side(order_side: str) -> int:
    if order_side == 'Sell':
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
        'price': float(raw_data.get('price')),
        'created': raw_data.get('timestamp'),
        'active': raw_data.get('ordStatus') != "New"
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


def load_quote_data(raw_data: dict) -> dict:
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'price': float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
    }


def load_quote_bin_data(raw_data: dict) -> dict:
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'open': float(raw_data.get("open")),
        'close': float(raw_data.get("close")),
        'high': float(raw_data.get("high")),
        'low': float(raw_data.get('low')),
        'volume': raw_data.get('volume'),
    }
