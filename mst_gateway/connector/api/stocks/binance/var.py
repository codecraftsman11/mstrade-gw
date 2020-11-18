from .... import api

BINANCE_MAX_QUOTE_BINS_COUNT = 1000

BINANCE_WALLET_TYPES = [
    api.OrderSchema.exchange,
    api.OrderSchema.margin2,
    api.OrderSchema.futures
]

BINANCE_ORDER_SIDE_BUY = 'BUY'
BINANCE_ORDER_SIDE_SELL = 'SELL'

BINANCE_ORDER_STATUS_NEW = 'NEW'

BINANCE_ORDER_DELETE_ACTION_STATUSES = ('FILLED', 'CANCELED', 'EXPIRED', 'REJECTED')

BINANCE_ORDER_STATUS_MAP = {
    'PARTIALLY_FILLED': api.OrderState.active,
    'NEW': api.OrderState.pending,
    'FILLED': api.OrderState.closed,
    'EXPIRED': api.OrderState.closed,
}

PARAMETER_NAMES_MAP = {
    'order_id': 'newClientOrderId',
    'exchange_order_id': 'orderId',
    'order_type': 'type',
    'volume': 'quantity',
    'iceberg_volume': 'icebergQty',
    'stop_price': 'stopPrice',
    'ttl': 'timeInForce',
}

UPDATED_PARAMETER_NAMES_MAP = {
    'order_id': 'origClientOrderId',
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
    }
}
