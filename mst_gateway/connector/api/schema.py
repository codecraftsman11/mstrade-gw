# pylint: disable=broad-except
from ..api.validators import (
    datetime_valid,
    iso_datetime_valid,
    pair_valid,
    side_valid,
    type_valid,
    schema_valid,
    execution_valid,
    exchange_order_id_valid,
    leverage_type_valid,
)
from mst_gateway.connector.api.types import OrderSchema


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
    'volume': str,
    'open_price': float,
    'close_price': float,
    'high_price': float,
    'low_price': float,
    'schema': (schema_valid, None),
    'symbol': (str, None),
    'system_symbol': (str, None),
}

SYMBOL_FIELDS = {
    'time': datetime_valid,
    'symbol': str,
    'schema': schema_valid,
    'price': float,
    'price24': float,
    'delta': float,
    'face_price': float,
    'bid_price': float,
    'ask_price': float,
    'reversed': bool,
    'volume24': float,
    'mark_price': float,
    'high_price': float,
    'low_price': float,
    'expiration': (str, None),
    'expiration_date': (datetime_valid, None),
    'pair': (pair_valid, None),
    'tick': (float, None),
    'volume_tick': (float, None),
    'system_symbol': (str, None),
    'symbol_schema': (schema_valid, None),
    'created': (datetime_valid, None),
    'max_leverage': (float, None),
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
    'stop': float,    # trigger level for Stop and Take Profit orders
    'type': type_valid,
    'side': str,
    'price': float,
    'time': datetime_valid,
    'active': bool,
    'schema': (schema_valid, None),
    'execution': execution_valid,
    'system_symbol': (str, None),
}

ORDER_BOOK_FIELDS = {
    'id': (int, None),
    'symbol': str,
    'price': float,
    'volume': float,
    'side': side_valid,
    'schema': (schema_valid, None),
    'system_symbol': (str, None),
}

TRADE_FIELDS = {
    'time': datetime_valid,
    'volume': str,
    'price': float,
    'side': side_valid,
    'schema': (schema_valid, None),
    'symbol': (str, None),
    'system_symbol': (str, None),
}

WALLET_FIELDS = {
    OrderSchema.margin1: {
        'currency': str,
        'balance': float,
        'withdraw_balance': float,
        'unrealised_pnl': float,
        'margin_balance': float,
        'maint_margin': float,
        'init_margin': float,
        'available_margin': float,
        'type': str,
    },
    OrderSchema.exchange: {
        'balances': list,
        'total_balance': dict,
    },
    OrderSchema.futures: {
        'trade_enabled': bool,
        'balances': list,
        'total_balance': dict,
        'total_unrealised_pnl': dict,
        'total_margin_balance': dict,
        'total_borrowed': dict,
        'total_interest': dict,
        'total_initial_margin': float,
        'total_maint_margin': float,
        'total_open_order_initial_margin': float,
        'total_position_initial_margin': float,
    },
    OrderSchema.futures_coin: {
        'trade_enabled': bool,
        'balances': list,
        'total_balance': dict,
        'total_unrealised_pnl': dict,
        'total_margin_balance': dict,
        'total_borrowed': dict,
        'total_interest': dict,
    },
}
BASE_BALANCE_FIELDS = {
    'currency': str,
    'balance': float,
    'withdraw_balance': float,
    'unrealised_pnl': float,
    'margin_balance': float,
    'maint_margin': float,
    'init_margin': (float, None),
    'available_margin': float,
    'type': str,
}
BALANCE_FIELDS = {
    OrderSchema.exchange: {
        **BASE_BALANCE_FIELDS,
    },
    OrderSchema.futures: {
        'borrowed': float,
        'interest': float,
        **BASE_BALANCE_FIELDS,
    },
    OrderSchema.futures_coin: {
        'borrowed': float,
        'interest': float,
        **BASE_BALANCE_FIELDS,
    },
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
    'maker': float,
    'taker': float,
    'type': str,
}

BASE_WALLET_DETAIL_FIELDS = {
    'currency': str,
    'balance': float,
    'withdraw_balance': float,
    'unrealised_pnl': float,
    'margin_balance': float,
    'maint_margin': float,
    'init_margin': (float, None),
    'available_margin': float,
    'type': str,
}
WALLET_DETAIL_FIELDS = {
    OrderSchema.exchange: {
        **BASE_WALLET_DETAIL_FIELDS,
    },
    OrderSchema.futures: {
        'borrowed': float,
        'interest': float,
        'cross_collaterals': list,
        **BASE_WALLET_DETAIL_FIELDS,
    },
    OrderSchema.futures_coin: {
        'borrowed': float,
        'interest': float,
        'cross_collaterals': list,
        **BASE_WALLET_DETAIL_FIELDS,
    },
}

BASE_EXCHANGE_SYMBOL_INFO_FIELDS = {
    'symbol': str,
    'system_symbol': str,
    'schema': schema_valid,
    'symbol_schema': schema_valid,
    'base_asset': str,
    'quote_asset': str,
    'system_base_asset': str,
    'system_quote_asset': str,
    'pair': pair_valid,
    'system_pair': pair_valid,
    'tick': float,
    'volume_tick': float,
    'expiration': (str, None),
    'expiration_date': (datetime_valid, None),
    'max_leverage': (float, None),
}
EXCHANGE_SYMBOL_INFO_FIELDS = {
    OrderSchema.exchange: {
        **BASE_EXCHANGE_SYMBOL_INFO_FIELDS,
    },
    OrderSchema.futures: {
        'leverage_brackets': list,
        **BASE_EXCHANGE_SYMBOL_INFO_FIELDS,
    },
    OrderSchema.futures_coin: {
        'leverage_brackets': list,
        **BASE_EXCHANGE_SYMBOL_INFO_FIELDS,
    },
}
BASE_LEVERAGE_BRACKETS_FIELDS = {
    'bracket': int,
    'initialLeverage': int,
    'maintMarginRatio': float,
    'cum': float,
}
LEVERAGE_BRACKET_FIELDS = {
    OrderSchema.futures: {
        'notionalCap': int,
        'notionalFloor': int,
        **BASE_LEVERAGE_BRACKETS_FIELDS,
    },
    OrderSchema.futures_coin: {
        'qtyCap': int,
        'qtyFloor': int,
        **BASE_LEVERAGE_BRACKETS_FIELDS,
    },
}

CURRENCY_EXCHANGE_SYMBOL_FIELDS = {
    'symbol': str,
    'price': float,
}

SYMBOL_CURRENCY_FIELDS = {
    'pair': pair_valid,
    'price': float,
    'expiration': (str, None),
}

WALLET_SUMMARY_FIELDS = {
    'total_balance': dict,
    'total_unrealised_pnl': dict,
    'total_margin_balance': dict,
}
SUMMARY_FIELDS = {
    'btc': float,
    'usd': float,
}

ALT_CURRENCY_COMMISSION_FIELDS = {
    'is_active': bool,
    'currency': str,
}

FUNDING_RATE_FIELDS = {
    'symbol': str,
    'funding_rate': float,
    'time': datetime_valid,
}

POSITION_FIELDS = {
    'time': datetime_valid,
    'schema': schema_valid,
    'symbol': str,
    'side': (side_valid, None),
    'volume': float,
    'entry_price': float,
    'mark_price': float,
    'unrealised_pnl': float,
    'leverage_type': leverage_type_valid,
    'leverage': float,
    'liquidation_price': float,
}

POSITION_STATE_FIELDS = {
    'symbol': str,
    'volume': float,
    'side': (side_valid, None),
    'entry_price': float,
    'mark_price': float,
    'leverage_type': leverage_type_valid,
    'leverage': float,
    'isolated_wallet_balance': float,
    'cross_wallet_balance': float,
    'action': str,
}

LIQUIDATION_FIELDS = {
    'liquidation_price': (float, None)
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
    if isinstance(rule, tuple) and len(rule) == 2 and rule[1] is None and value is None:
        return True
    if isinstance(rule, type):
        try:
            return value is None or isinstance(value, rule)
        except Exception:
            return False
    if callable(rule):
        return rule(value)
    return True
