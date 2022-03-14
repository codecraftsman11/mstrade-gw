from .... import api


BINANCE_THROTTLE_LIMITS = {
    'ws': 60,
    'rest': 1000,
    'order': 100
}

BINANCE_MAX_QUOTE_BINS_COUNT = 1000
BINANCE_MAX_ORDER_BOOK_LIMIT = 1000

BINANCE_WALLET_TYPES = [
    api.OrderSchema.exchange,
    api.OrderSchema.margin2,
    api.OrderSchema.margin3,
    api.OrderSchema.futures,
    api.OrderSchema.futures_coin,
]

BINANCE_ORDER_SIDE_BUY = 'BUY'
BINANCE_ORDER_SIDE_SELL = 'SELL'

BINANCE_ORDER_STATUS_NEW = 'NEW'

BINANCE_ORDER_DELETE_ACTION_STATUSES = ('FILLED', 'CANCELED', 'EXPIRED', 'REJECTED')

BINANCE_ORDER_STATUS_MAP = {
    'NEW': api.OrderState.pending,
    'PARTIALLY_FILLED': api.OrderState.active,
    'FILLED': api.OrderState.closed,
    'CANCELED': api.OrderState.closed,
    'EXPIRED': api.OrderState.expired,
    'REJECTED': api.OrderState.closed,
    'NEW_INSURANCE': api.OrderState.liquidated,
    'NEW_ADL': api.OrderState.liquidated
}

PARAMETER_NAMES_MAP = {
    'order_id': 'newClientOrderId',
    'exchange_order_id': 'orderId',
    'order_type': 'type',
    'volume': 'quantity',
    'iceberg_volume': 'icebergQty',
    'stop_price': 'stopPrice',
    'ttl': 'timeInForce',
    'H1': 'GTC',
    'H4': 'GTC',
    'D1': 'GTC',
    'GTC': 'GTC',
    'FOK': 'FOK',
    'IOC': 'IOC',
    'GTX': 'GTX'
}


DEFAULT_PARAMETERS = [
    'newClientOrderId',
    'symbol',
    'type',
    'side',
    'quantity',
    'quoteOrderQty'
]

PARAMETERS_BY_ORDER_TYPE_MAP = {

    api.OrderSchema.futures_coin: {
        'MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'reduceOnly',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        },
    },

    api.OrderSchema.futures: {
        'MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'reduceOnly',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        },
    },

    api.OrderSchema.exchange: {
        'MARKET': {
            'params': [
                *DEFAULT_PARAMETERS
            ],
            'additional_params': {}
        },
        'LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'icebergQty',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        },
    },

    api.OrderSchema.margin2: {
        'MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'isIsolated',
                'sideEffectType'
            ],
            'additional_params': {}
        },
        'LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'isIsolated',
                'sideEffectType'
                'icebergQty',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        }
    },

    api.OrderSchema.margin3: {
        'MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'isIsolated',
                'sideEffectType'
            ],
            'additional_params': {}
        },
        'LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'isIsolated',
                'sideEffectType'
                'icebergQty',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        }
    }
}

BINANCE_LEVERAGE_TYPE_CROSS = "CROSSED"
BINANCE_LEVERAGE_TYPE_ISOLATED = "ISOLATED"


class BinancePositionSideMode:
    BOTH = 'BOTH'
    LONG = 'LONG'
    SHORT = 'SHORT'
