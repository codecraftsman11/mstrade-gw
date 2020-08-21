# pylint: disable=broad-except
from ..api.validators import (
    datetime_valid,
    pair_valid,
    side_valid,
    order_id_valid,
    type_valid,
    schema_valid
)


QUOTE_FIELDS = {
    'time': datetime_valid,
    'timestamp': int,
    'symbol': str,
    'volume': int,
    'price': float,
    'side': side_valid,
    'schema': schema_valid,
    'system_symbol': str,
}

QUOTE_BIN_FIELDS = {
    'time': datetime_valid,
    'timestamp': int,
    'symbol': str,
    'volume': int,
    'open': float,
    'high': float,
    'low': float,
    'close': float,
    'schema': schema_valid,
    'system_symbol': str,
}

SYMBOL_FIELDS = {
    'time': datetime_valid,
    'timestamp': int,
    'pair': pair_valid,
    'symbol': str,
    'expiration': str,
    'price': float,
    'price24': float,
    'tick': float,
    'mark_price': float,
    'face_price': float,
    'bid_price': float,
    'ask_price': float,
    'reversed': bool,
    'schema': schema_valid,
    'system_symbol': str,
    'symbol_schema': schema_valid
}

ORDER_FIELDS = {
    'order_id': order_id_valid,
    'symbol': str,
    'value': int,
    'stop': float,
    'type': type_valid,
    'side': side_valid,
    'price': float,
    'created': datetime_valid,
    'active': bool,
    'schema': schema_valid,
    'system_symbol': str,
}

ORDER_BOOK_FIELDS = {
    'id': int,
    'symbol': str,
    'price': float,
    'volume': int,
    'side': side_valid,
    'schema': schema_valid,
    'system_symbol': str,
}

TRADE_FIELDS = {
    'time': datetime_valid,
    'timestamp': int,
    'symbol': str,
    'volume': int,
    'price': float,
    'side': side_valid,
    'schema': schema_valid,
    'system_symbol': str,
}

WALLET_FIELDS = {
    'currency': str,
    'balance': float,
    'withdraw_balance': float,
    'borrowed': float,
    'available_borrow': float,
    'interest': float,
    'interest_rate': float,
    'unrealised_pnl': float,
    'margin_balance': float,
    'maint_margin': float,
    'init_margin': float,
    'available_margin': float,
    'type': str
}

WALLET_MARGIN1_FIELDS = {
    'currency': str,
    'balance': float,
    'withdraw_balance': float,
    'unrealised_pnl': float,
    'margin_balance': float,
    'maint_margin': float,
    'init_margin': float,
    'available_margin': float,
    'type': str
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
    },
    'order_book': {
        'schema': ORDER_BOOK_FIELDS
    },
    'trade': {
        'schema': TRADE_FIELDS
    },
}

AUTH_SUBSCRIPTIONS = {
    'order': {
        'schema': ORDER_FIELDS
    }
}

USER_FIELDS = {
    'id': str
}

ORDER_COMMISSION = {
    "currency": str,
    "taker": float,
    "maker": float,
    "type": str
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
