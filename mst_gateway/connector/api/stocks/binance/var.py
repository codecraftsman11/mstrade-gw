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
    api.OrderSchema.margin_cross,
    api.OrderSchema.margin_isolated,
    api.OrderSchema.margin,
    api.OrderSchema.margin_coin,
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

BINANCE_ORDER_TTL_MAP = {
    'IOC': api.OrderTTL.IOC,
    'FOK': api.OrderTTL.FOK,
    'GTC': api.OrderTTL.GTC,
    'GTX': api.OrderTTL.GTC
}

BASE_PARAMETER_NAMES_MAP = {
    'order_id': 'origClientOrderId',
    'exchange_order_id': 'orderId',
    'order_type': 'type',
    'volume': 'quantity',
    'iceberg_volume': 'icebergQty',
    'stop_price': 'stopPrice',
    'reduce_only': 'reduceOnly',
    'new_order_resp_type': 'newOrderRespType',
    'position_side': 'positionSide',
    'ttl': 'timeInForce',
    'H1': 'GTC',
    'H4': 'GTC',
    'D1': 'GTC',
    'GTC': 'GTC',
    'FOK': 'FOK',
    'IOC': 'IOC',
    'GTX': 'GTX'
}

SPOT_PARAMETER_NAMES_MAP = {
    **BASE_PARAMETER_NAMES_MAP,
    'step': 'trailingDelta',
}

FUTURES_PARAMETER_NAMES_MAP = {
    **BASE_PARAMETER_NAMES_MAP,
    'step': 'callbackRate'
}

CREATE_PARAMETER_NAMES_MAP = {
    'order_id': 'newClientOrderId',
}

DEFAULT_PARAMETERS = [
    'newClientOrderId',
    'newOrderRespType',
    'symbol',
    'type',
    'side',
    'quantity',
    'quoteOrderQty'
]

PARAMETERS_BY_ORDER_TYPE_MAP = {
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
        'STOP_LOSS_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'timeInForce',
                'price'
            ],
            'additional_params': {}
        },
        'STOP_LOSS': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'quantity'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'timeInForce',
                'stopPrice',
                'price',
                'quantity'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
            ],
            'additional_params': {}
        },
        'TRAILING_STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'trailingDelta',
                'reduceOnly'
            ],
            'additional_params': {
                'type': 'STOP_LOSS'
            }
        }
    },

    api.OrderSchema.margin_cross: {
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
        },
        'STOP_LOSS_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'trailingDelta',
                'timeInForce',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'STOP_LOSS': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'quantity',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'timeInForce',
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TRAILING_STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'trailingDelta',
                'reduceOnly'
            ],
            'additional_params': {
                'type': 'STOP_LOSS'
            }
        }
    },

    api.OrderSchema.margin_isolated: {
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
        },
        'STOP_LOSS_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'trailingDelta',
                'timeInForce',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'STOP_LOSS': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'quantity',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT_LIMIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'timeInForce',
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TRAILING_STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'trailingDelta',
                'reduceOnly'
            ],
            'additional_params': {
                'type': 'STOP_LOSS'
            }
        }
    },

    api.OrderSchema.margin: {
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
        'STOP': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'stopPrice',
                'quantity',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly',
                'positionSide'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'quantity',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TRAILING_STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'callbackRate',
                'stopPrice',
                'activationPrice',
                'reduceOnly'
            ],
            'additional_params': {
                'callbackRate': 1
            }
        }
    },

    api.OrderSchema.margin_coin: {
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
        'STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly',
                'positionSide'
            ],
            'additional_params': {}
        },
        'STOP': {
            'params': [
                *DEFAULT_PARAMETERS,
                'positionSide',
                'stopPrice',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'price',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TAKE_PROFIT_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPrice',
                'reduceOnly'
            ],
            'additional_params': {}
        },
        'TRAILING_STOP_MARKET': {
            'params': [
                *DEFAULT_PARAMETERS,
                'activationPrice',
                'stopPrice',
                'callbackRate',
                'reduceOnly'
            ],
            'additional_params': {
                'callbackRate': 1
            }
        }
    }

}

BINANCE_LEVERAGE_TYPE_CROSS = "CROSSED"
BINANCE_LEVERAGE_TYPE_ISOLATED = "ISOLATED"
