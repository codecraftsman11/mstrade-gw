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
    exchange_order_id_valid,
    leverage_type_valid,
    state_valid,
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
    'time': Use(datetime_valid),
    'volume': str,
    'open_price': float,
    'close_price': float,
    'high_price': float,
    'low_price': float,
    'schema': Or(None, Use(schema_valid)),
    'symbol': Or(None, str),
    'system_symbol': Or(None, str),
}

SYMBOL_FIELDS = {
    'time': Use(datetime_valid),
    'symbol': str,
    'schema': Use(schema_valid),
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
    'expiration': Or(None, str),
    'expiration_date': Or(None, Use(datetime_valid), str),
    'pair': Or(None, Use(pair_valid)),
    'tick': Or(None, float),
    'volume_tick': Or(None, float),
    'system_symbol': Or(None, str),
    'symbol_schema': Or(None, Use(schema_valid)),
    'created': Or(None, Use(datetime_valid)),
    'max_leverage': Or(None, float),
}

ORDER_FIELDS = {
    'exchange_order_id': Use(exchange_order_id_valid),
    'symbol': str,
    'volume': float,
    'filled_volume': float,
    'stop': float,    # trigger level for Stop and Take Profit orders
    'type': Use(type_valid),
    'side': str,
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
    'volume': float,
    'side': Use(side_valid),
    'schema': Or(None, Use(schema_valid)),
    'system_symbol': Or(None, str),
}

TRADE_FIELDS = {
    'time': Use(datetime_valid),
    'volume': str,
    'price': float,
    'side': Use(side_valid),
    'schema': Or(None, Use(schema_valid)),
    'symbol': Or(None, str),
    'system_symbol': Or(None, str),
}

WALLET_FIELDS = {
    OrderSchema.margin1: {
        'currency': str,
        'balance': float,
        'withdraw_balance': float,
        'unrealised_pnl': float,
        'margin_balance': float,
        'maint_margin': float,
        'init_margin': Or(None, float),
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
    'init_margin': Or(None, float),
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
    'init_margin': Or(None, float),
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
    'schema': Use(schema_valid),
    'symbol_schema': Use(schema_valid),
    'base_asset': str,
    'quote_asset': str,
    'system_base_asset': str,
    'system_quote_asset': str,
    'pair': Use(pair_valid),
    'system_pair': Use(pair_valid),
    'tick': float,
    'volume_tick': float,
    'expiration': Or(None, str),
    'expiration_date': Or(None, Use(datetime_valid)),
    'max_leverage': Or(None, float),
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
    'pair': Use(pair_valid),
    'price': float,
    'expiration': Or(None, str),
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
    'time': Use(datetime_valid),
}

POSITION_FIELDS = {
    'time': Use(datetime_valid),
    'schema': Use(schema_valid),
    'symbol': str,
    'side': Or(None, Use(side_valid)),
    'volume': float,
    'entry_price': float,
    'mark_price': float,
    'unrealised_pnl': float,
    'leverage_type': Use(leverage_type_valid),
    'leverage': float,
    'liquidation_price': float,
}

POSITION_STATE_FIELDS = {
    'symbol': str,
    'volume': float,
    'side': Or(None, Use(side_valid)),
    'entry_price': float,
    'mark_price': Or(None, float),
    'leverage_type': Use(leverage_type_valid),
    'leverage': float,
    'isolated_wallet_balance': float,
    'cross_wallet_balance': Or(None, float),
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
        'eoid': int,
        'sd': Use(side_valid),
        'tv': float,
        'tp': float,
        'vl': float,
        'p': float,
        'st': Use(state_valid),
        'lv': float,
        'fv': float,
        'ap': float,
        'tm': Or(None, iso_datetime_valid),
        's': str,
        'stp': float,
        'crt': Or(None, Use(datetime_valid)),
        't': Use(type_valid),
        'exc': Use(execution_valid),
        'ss': Or(None, str),
    },
    'order_book': {
        'id': Or(None, int),
        's': str,
        'ss': Or(None, str),
        'sd': Use(side_valid),
        'vl': float,
        'p': float,
    },
    'position': {

    },
    'quote_bin': {
        'tm': Or(None, Use(iso_datetime_valid)),
        's': Or(None, str),
        'ss': Or(None, str),
        'vl': float,
        'opp': float,
        'clp': float,
        'hip': float,
        'lop': float,
    },
    'symbol': {
        'tm': Or(None, Use(iso_datetime_valid)),
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
        'v24': float,
        'mp': float,
        'hip': float,
        'lop': float,
        'exp': Or(None, str),
        'expd': Or(None, Use(iso_datetime_valid)),
        'pa': Or(None, Use(pair_valid)),
        'tck': Or(None, float),
        'vt': Or(None, float),
        'crt': Or(None, Use(datetime_valid)),
        'mlvr': Or(None, float),
    },
    'trade': {
        'tm': Or(None, Use(iso_datetime_valid)),
        's': str,
        'ss': Or(None, str),
        'sd': Use(side_valid),
        'vl': float,
        'p': float,
    },
    'wallet': {
        OrderSchema.exchange: {
            'tbl': dict,
            'bls': list,
        },
        OrderSchema.futures: {
            'tre': bool,
            'tbl': dict,
            'tupnl': dict,
            'tmbl': dict,
            'tbor': dict,
            'tist': dict,
            'tim': float,
            'tmm': float,
            'toip': float,
            'tpim': float,
            'bls': list,
        },
        OrderSchema.futures_coin: {
            'tre': bool,
            'tbl': dict,
            'tupnl': dict,
            'tmbl': dict,
            'tbor': dict,
            'tist': dict,
            'bls': list,
        },
    },
    'balance': {
        OrderSchema.exchange: {
            'cur': str,
            'bl': float,
            'upnl': Or(None, float, int),
            'mbl': float,
            'mm': float,
            'im': Or(None, float, int),
            'am': float,
            't': str,
        },
        OrderSchema.futures: {
            'cur': str,
            'bl': float,
            Optional('wbl'): Or(None, float, int),
            'bor': Or(None, float, int),
            'ist': Or(None, float, int),
            'upnl': Or(None, float, int),
            'mbl': Or(None, float, int),
            'mm': Or(None, float, int),
            'im': Or(None, float, int),
            'am': Or(None, float, int),
            't': str,
        },
        OrderSchema.futures_coin: {
            'cur': str,
            'bl': float,
            'wbl': Or(None, float, int),
            'bor': Or(None, float, int),
            'ist': Or(None, float, int),
            'upnl': Or(None, float, int),
            'mbl': Or(None, float, int),
            'mm': Or(None, float, int),
            'im': Or(None, float, int),
            'am': Or(None, float, int),
            't': str,
        },
    },
}
