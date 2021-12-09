from datetime import datetime, timezone
from mst_gateway.connector.api.types import OrderExec, OrderSchema, OrderType, OrderTTL, BUY, SELL

DEFAULT_ORDER_SIDE = BUY
DEFAULT_ORDER_SIDE_STR = 'BUY'
DEFAULT_ORDER_OPPOSITE_SIDE = SELL
DEFAULT_ORDER_OPPOSITE_SIDE_STR = 'SELL'
DEFAULT_ORDER_VOLUME = {
    OrderSchema.exchange: 0.001,
    OrderSchema.futures: 0.001,
    OrderSchema.futures_coin: 1.0,
}
DEFAULT_ORDER_OPTIONS = {
    'ttl': OrderTTL.GTC,
    'is_passive': False,
    'is_iceberg': False,
    'iceberg_volume': None,
    'comments': '',
}
DEFAULT_ORDER = {
    OrderSchema.exchange: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.exchange,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSDT',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
    },
    OrderSchema.futures: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.futures,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSDT',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.futures],
    },
    OrderSchema.futures_coin: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.futures_coin,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSD_PERP',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
    },
}


DEFAULT_ORDER_MESSAGE = {
    OrderSchema.exchange: {

    },
    OrderSchema.futures: {

    },
    OrderSchema.futures_coin: {

    },
}
DEFAULT_ORDER_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {

    },
    OrderSchema.futures: {

    },
    OrderSchema.futures_coin: {

    },
}
DEFAULT_ORDER_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [

    ],
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
DEFAULT_ORDER_GET_DATA_RESULT = {
    OrderSchema.exchange: [

    ],
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
