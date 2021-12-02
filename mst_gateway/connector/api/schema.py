# pylint: disable=broad-except
from . import OrderSchema
from ..api.validators import (
    datetime_valid,
    iso_datetime_valid,
    pair_valid,
    side_valid,
    type_valid,
    schema_valid,
    execution_valid,
    exchange_order_id_valid
)

ASSET = "XBT"

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
    'symbol': str,
    'open_price': float,
    'close_price': float,
    'high_price': float,
    'low_price': float,
    'volume': int,
    'system_symbol': str,
    'schema': schema_valid,
}

SYMBOL_FIELDS = {
    'time': datetime_valid,
    'symbol': str,
    'price': float,
    'price24': float,
    'delta': float,
    'face_price': float,
    'bid_price': float,
    'ask_price': float,
    'reversed': bool,
    'volume24': int,
    'mark_price': float,
    'high_price': float,
    'low_price': float,
    'expiration': str,
    'expiration_date': str,
    'pair': pair_valid,
    'tick': float,
    'volume_tick': float,
    'system_symbol': str,
    'schema': schema_valid,
    'symbol_schema': schema_valid,
    'created': datetime_valid,
    'max_leverage': float,
}

WS_SYMBOL_FIELDS = {
    'time': iso_datetime_valid,
    'timestamp': int,
    'pair': pair_valid,
    'symbol': str,
    'expiration': str,
    'price': float,
    'price24': float,
    'delta': float,
    'tick': float,
    'volume_tick': float,
    'face_price': float,
    'bid_price': float,
    'ask_price': float,
    'reversed': bool,
    'volume24': int,
    'schema': schema_valid,
    'system_symbol': str,
    'symbol_schema': schema_valid,
    'created': iso_datetime_valid,
    'max_leverage': float,
}

ORDER_FIELDS = {
    'exchange_order_id': exchange_order_id_valid,
    'symbol': str,
    'volume': float,
    'filled_volume': float,
    'stop': float,  # trigger level for Stop and Take Profit orders
    'side': side_valid,
    'price': float,
    'time': datetime_valid,
    'active': bool,
    'type': type_valid,
    'execution': execution_valid,
    'system_symbol': str,
    'schema': schema_valid,
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
    'symbol': str,
    'price': float,
    'volume': int,
    'side': side_valid,
    'system_symbol': str,
    'schema': schema_valid,
}

WALLET_FIELDS = {
    'balances': list,
    'total_balance': dict,
    'total_unrealised_pnl': dict,
    'total_margin_balance': dict
}

WALLET_SUMMARY_FIELDS = {
    'total_balance': dict,
    'total_unrealised_pnl': dict,
    'total_margin_balance': dict
}

BASE_WALLET_DETAIL_FIELDS = {
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

WALLET_DETAIL_FIELDS = {
    OrderSchema.margin1: {
        **BASE_WALLET_DETAIL_FIELDS
    },
}

ASSETS_BALANCE = {
    OrderSchema.margin1: {
        ASSET.lower(): float
    }
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

ORDER_COMMISSION_FIELDS = {
    "symbol": str,
    "taker": float,
    "maker": float,
    "type": str
}

EXCHANGE_SYMBOL_INFO_FIELDS = {
    OrderSchema.margin1: {
        'symbol': str,
        'system_symbol': str,
        'base_asset': str,
        'quote_asset': str,
        'system_base_asset': str,
        'system_quote_asset': str,
        'expiration': str,
        'expiration_date': datetime_valid,
        'pair': list,
        'system_pair': list,
        'schema': schema_valid,
        'symbol_schema': schema_valid,
        'tick': float,
        'volume_tick': float,
        'max_leverage': float
    }
}

CURRENCY_EXCHANGE_SYMBOL_FIELDS = {
    'symbol': str,
    'price': float
}

SYMBOL_CURRENCY_FIELDS = {
    'pair': list,
    'expiration': str,
    'price': float
}

FUNDING_RATE_FIELDS = {
    'symbol': str,
    'funding_rate': float,
    'time': datetime_valid
}

POSITION_FIELDS = {
    'schema': str,
    'symbol': str,
    'side': int,
    'volume': float,
    'entry_price': float,
    'mark_price': float,
    'unrealised_pnl': float,
    'leverage_type': str,
    'leverage': float,
    'liquidation_price': float
}

LIQUIDATION_PRICE_FIELDS = {
    'liquidation_price': float
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
