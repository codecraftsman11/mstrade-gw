# pylint: disable=broad-except
from datetime import datetime
from .. import api


QUOTE_FIELDS = {
    "timestamp": datetime,
    "symbol": str,
    "volume": int,
    "price": float,
    "side": api.side_valid,
}

QUOTE_BIN_FIELDS = {
    "timestamp": datetime,
    "symbol": str,
    "volume": int,
    "open": float,
    "high": float,
    "low": float,
    "close": float,
}

SYMBOL_FIELDS = {
    'timestamp': datetime,
    'symbol': str,
    'price': float
}

ORDER_FIELDS = {
    'order_id': api.order_id_valid,
    'symbol': str,
    'value': int,
    'stop': float,
    'type': api.type_valid,
    'side': api.side_valid,
    'price': float,
    'created': datetime,
    'active': bool
}

SUBSCRIPTIONS = {
    'symbol': {
        'schema': SYMBOL_FIELDS,
    },
    'quote': {
        'schema': QUOTE_FIELDS
    },
    'quote_bin': {
        'schema': QUOTE_BIN_FIELDS
    }
}

AUTH_SUBSCRIPTIONS = {
    'order': {
        'schema': ORDER_FIELDS
    }
}


def data_valid(data, rules):
    if not isinstance(data, dict):
        raise TypeError("Data is not dictionary")
    if not set(data.keys()) == set(rules.keys()):
        raise ValueError("Keys differ")
    for k in data:
        if not value_valid(data[k], rules[k]):
            raise ValueError("Invalid {}".format(k))
    return True


def data_update_valid(data, rules):
    if not isinstance(data, dict):
        raise TypeError("Data is not dictionary")
    if set(data.keys()) - set(rules.keys()):
        raise ValueError("In data present keys out of rule's range")
    for k in data:
        if not value_valid(data[k], rules[k]):
            raise ValueError("Invalid {}".format(k))
    return True


def value_valid(value, rule):
    if isinstance(rule, type):
        try:
            return value is None or isinstance(value, rule)
        except Exception:
            return False
    if callable(rule):
        return rule(value)
    return True
