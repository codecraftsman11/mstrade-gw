# pylint: disable=broad-except
from schema import Use, Or, Optional
from .validators import (
    datetime_valid,
    iso_datetime_valid,
    pair_valid,
    side_valid,
    type_valid,
    schema_valid,
    execution_valid,
    leverage_type_valid,
    state_valid,
    float_valid,
)
from mst_gateway.connector.api.types import OrderSchema

QUOTE_BIN_FIELDS = {
    'time': Use(datetime_valid),
    'volume': Or(int, str),
    'open_price': Use(float_valid),
    'close_price': Use(float_valid),
    'high_price': Use(float_valid),
    'low_price': Use(float_valid),
    'schema': Or(None, Use(schema_valid)),
    'symbol': Or(None, str),
    'system_symbol': Or(None, str),
}

SYMBOL_FIELDS = {
    'time': Use(datetime_valid),
    'symbol': str,
    'schema': Use(schema_valid),
    'price': Use(float_valid),
    'price24': Use(float_valid),
    'delta': Use(float_valid),
    'face_price': Use(float_valid),
    'bid_price': Use(float_valid),
    'ask_price': Use(float_valid),
    'reversed': bool,
    'volume24': Or(int, float),
    'mark_price': Use(float_valid),
    'high_price': Use(float_valid),
    'low_price': Use(float_valid),
    'expiration': Or(None, str),
    'expiration_date': Or(None, Use(datetime_valid), str),
    'pair': Or(None, Use(pair_valid)),
    'tick': Or(None, float),
    'volume_tick': Or(None, float),
    'system_symbol': Or(None, str),
    'symbol_schema': Or(None, Use(schema_valid)),
    'created': Or(None, Use(datetime_valid)),
    'max_leverage': Or(None, float),
    'wallet_asset': Or(None, str),
}

ORDER_FIELDS = {
    'exchange_order_id': str,
    'symbol': str,
    'volume': Or(int, float),
    'filled_volume': Use(float_valid),
    'stop': Or(None, float),  # trigger level for Stop and Take Profit orders
    'type': Use(type_valid),
    'side': int,
    'price': float,
    'time': Use(datetime_valid),
    'active': bool,
    'schema': Or(None, Use(schema_valid)),
    'execution': Use(execution_valid),
    'system_symbol': Or(None, str),
}

ORDER_BOOK_FIELDS = {
    'id': Or(None, int),
    'symbol': str,
    'price': float,
    'volume': Or(int, float),
    'side': Use(side_valid),
    'schema': Or(None, Use(schema_valid)),
    'system_symbol': Or(None, str),
}

TRADE_FIELDS = {
    'time': Use(datetime_valid),
    'volume': Use(float_valid),
    'price': float,
    'side': Use(side_valid),
    'schema': Or(None, Use(schema_valid)),
    'symbol': Or(None, str),
    'system_symbol': Or(None, str),
}
WALLET_FIELDS = {
    'balances': list,
    'total_balance': dict,
    'total_unrealised_pnl': dict,
    'total_margin_balance': dict,
    'extra_data': Or(None, dict)
}
WALLET_BALANCE_FIELDS = {
    'currency': str,
    'balance': Use(float_valid),
    'withdraw_balance': Use(float_valid),
    'unrealised_pnl': Use(float_valid),
    'margin_balance': Use(float_valid),
    'init_margin': Use(float_valid),
    'maint_margin': Use(float_valid),
    'available_margin': Use(float_valid),
    'type': str,
}

WALLET_EXTRA_FIELDS = {
    OrderSchema.margin2: {
        'balances': list,
        'trade_enabled': bool,
        'transfer_enabled': bool,
        'borrow_enabled': bool,
        'margin_level': Use(float_valid),
        'total_borrowed': dict,
        'total_interest': dict,
    },
    OrderSchema.futures: {
        'balances': list,
        'trade_enabled': bool,
        'total_borrowed': dict,
        'total_interest': dict,
    },
    OrderSchema.futures_coin: {
        'trade_enabled': bool
    }
}

WALLET_EXTRA_BALANCE_FIELDS = {
    OrderSchema.margin2: {
        'currency': str,
        'borrowed': Use(float_valid),
        'interest': Use(float_valid),
    },
    OrderSchema.futures: {
        'currency': str,
        'borrowed': Use(float_valid),
        'interest': Use(float_valid),
    }
}


WALLET_EXTRA_DATA_FIELDS = {
    OrderSchema.margin2: {
        'currency': str,
        'borrowed': Use(float_valid),
        'interest': Use(float_valid),
        'interest_rate': Use(float_valid),
        'available_borrow': Use(float_valid)
    },
    OrderSchema.futures: {
        'currency': str,
        'borrowed': Use(float_valid),
        'interest': Use(float_valid),
        'cross_collaterals': list
    }
}


USER_FIELDS = {
    'id': str
}

ORDER_COMMISSION_FIELDS = {
    Optional('symbol'): str,
    'maker': Use(float_valid),
    'taker': Use(float_valid),
    'type': str,
}

ASSETS_BALANCE = {
    str: Use(float_valid)
}

BASE_EXCHANGE_SYMBOL_INFO_FIELDS = {
    'symbol': str,
    'system_symbol': str,
    'schema': Use(schema_valid),
    'symbol_schema': Use(schema_valid),
    'base_asset': str,
    'quote_asset': str,
    'system_base_asset': str,
    'system_quote_asset': str,
    'pair': Use(pair_valid),
    'system_pair': Use(pair_valid),
    'tick': Use(float_valid),
    'volume_tick': Use(float_valid),
    'expiration': Or(None, str),
    'expiration_date': Or(None, Use(datetime_valid)),
    'max_leverage': Or(None, float),
    'wallet_asset': Or(None, str),
}
EXCHANGE_SYMBOL_INFO_FIELDS = {
    OrderSchema.margin1: {
        **BASE_EXCHANGE_SYMBOL_INFO_FIELDS,
    },
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
    'maintMarginRatio': Use(float_valid),
    'cum': Use(float_valid),
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
    'pair': Use(pair_valid),
    'price': float,
    'expiration': Or(None, str),
}

WALLET_SUMMARY_FIELDS = {
    'total_balance': dict,
    'total_unrealised_pnl': dict,
    'total_margin_balance': dict,
}
TOTAL_CROSS_AMOUNT_FIELDS = {
    'btc': Use(float_valid),
    'usd': Use(float_valid),
}

ALT_CURRENCY_COMMISSION_FIELDS = {
    'is_active': bool,
    'currency': str,
}

FUNDING_RATE_FIELDS = {
    'symbol': str,
    'funding_rate': Use(float_valid),
    'time': Use(datetime_valid),
}

POSITION_FIELDS = {
    'time': Use(datetime_valid),
    'schema': Use(schema_valid),
    'symbol': str,
    'side': Or(None, Use(side_valid)),
    'volume': Or(int, float),
    'entry_price': float,
    'mark_price': float,
    'unrealised_pnl': Use(float_valid),
    'leverage_type': Use(leverage_type_valid),
    'leverage': Use(float_valid),
    'liquidation_price': Use(float_valid),
}

POSITION_STATE_FIELDS = {
    'symbol': str,
    'volume': Or(int, float),
    'side': Or(None, Use(side_valid)),
    'entry_price': float,
    'mark_price': Or(None, float),
    'leverage_type': Use(leverage_type_valid),
    'leverage': Use(float_valid),
    'isolated_wallet_balance': Use(float_valid),
    'cross_wallet_balance': Use(float_valid),
    'action': str,
}

LIQUIDATION_FIELDS = {
    'liquidation_price': Or(None, float)
}

WS_MESSAGE_HEADER_FIELDS = {
    'acc': str,
    'tb': str,
    'sch': Use(schema_valid),
    'act': str,
    'd': list,
}

WS_MESSAGE_DATA_FIELDS = {
    'order': {
        'eoid': str,
        'sd': Use(side_valid),
        'tv': Or(None, float),
        'tp': Or(None, float),
        'vl': float,
        'p': float,
        'st': Use(state_valid),
        'lv': float,
        'fv': float,
        'ap': Or(None, float),
        'tm': Or(None, iso_datetime_valid),
        's': str,
        'stp': Or(None, float),
        Optional('crt'): Or(None, Use(datetime_valid)),
        't': Use(type_valid),
        'exc': Use(execution_valid),
        'ss': Or(None, str),
    },
    'order_book': {
        'id': Or(None, int),
        's': str,
        'ss': Or(None, str),
        'sd': Use(side_valid),
        'vl': Or(None, Use(float_valid)),
        'p': Or(None, float),
    },
    'position': {
        'tm': Use(iso_datetime_valid),
        's': str,
        'sd': Or(None, Use(side_valid)),
        'vl': float,
        'ep': Or(None, float),
        'mp': Or(None, float),
        'upnl': dict,
        'lvrp': Use(leverage_type_valid),
        'lvr': Use(float_valid),
        'lp': Or(None, float),
        'act': str,
        'ss': Or(None, str),
    },
    'quote_bin': {
        'tm': Use(iso_datetime_valid),
        's': Or(None, str),
        'ss': Or(None, str),
        'vl': Use(float_valid),
        'opp': float,
        'clp': float,
        'hip': float,
        'lop': float,
    },
    'symbol': {
        'tm': Use(iso_datetime_valid),
        's': str,
        'ss': Or(None, str),
        'ssch': Or(None, Use(schema_valid)),
        'p': float,
        'p24': float,
        'dt': float,
        'fp': float,
        'bip': float,
        'asp': float,
        're': bool,
        'v24': Use(float_valid),
        'mp': float,
        'hip': float,
        'lop': float,
        'exp': Or(None, str),
        'expd': Or(None, Use(iso_datetime_valid), str),
        'pa': Or(None, Use(pair_valid)),
        'tck': Use(float_valid),
        'vt': Use(float_valid),
        'crt': Or(None, Use(datetime_valid)),
        'mlvr': Use(float_valid),
        'wa': Or(None, str),
    },
    'trade': {
        'tm': Use(iso_datetime_valid),
        's': str,
        'ss': Or(None, str),
        'sd': Use(side_valid),
        'vl': Use(float_valid),
        'p': Use(float_valid)
    },
    'wallet': {
        'bls': list,
        'tbl': dict,
        'tupnl': dict,
        'tmbl': dict,
        'ex': Or(None, dict)
    }
}

WS_POSITION_CROSS_AMOUNT_FIELDS = {
    'base': Or(None, float),
    'usd': Or(None, float),
    'btc': Or(None, float),
}

WS_WALLET_BALANCE_FIELDS = {
    'cur': str,
    'bl': Use(float_valid),
    'wbl': Use(float_valid),
    'upnl': Use(float_valid),
    'mbl': Use(float_valid),
    'mm': Use(float_valid),
    'im': Use(float_valid),
    'am': Use(float_valid),
    't': str
}

WS_WALLET_EXTRA_FIELDS = {
    OrderSchema.margin2: {
        'bls': list,
        'tre': bool,
        'trse': bool,
        'bore': bool,
        'mlvl': Use(float_valid),
        'tbor': dict,
        'tist': dict
    },
    OrderSchema.futures: {
        'bls': list,
        'tre': bool,
        'tbor': dict,
        'tist': dict
    },
    OrderSchema.futures_coin: {
        'tre': bool
    }
}

WS_WALLET_EXTRA_BALANCE_FIELDS = {
    'cur': str,
    'bor': Use(float_valid),
    'ist': Use(float_valid)
}
