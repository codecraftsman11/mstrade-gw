from mst_gateway.connector import api


BITMEX_MAX_QUOTE_BINS_COUNT = 750

BITMEX_BUY = "Buy"
BITMEX_SELL = "Sell"

BITMEX_ORDER_STATUS_NEW = 'New'
BITMEX_ORDER_DELETE_ACTION_STATUSES = ('Filled', 'Canceled', 'PendingCancel', 'Stopped', 'Rejected', 'Expired')

BITMEX_ORDER_STATUS_MAP = {
    'PartiallyFilled': api.OrderState.active,
    'New': api.OrderState.pending,
    'Filled': api.OrderState.closed,
    'Canceled': api.OrderState.closed,
}

PARAMETER_NAMES_MAP = {
    'order_id': 'clOrdID',
    'exchange_order_id': 'orderID',
    'stop_price': 'stopPx',
    'volume': 'orderQty',
    'comments': 'text',
    'ttl': 'timeInForce',
    'ttl_type': 'timeInForce',
    'display_value': 'displayQty',
    'order_type': 'ordType',
    'is_passive': 'execInst',
    'iceberg_volume': 'displayQty'
}


DEFAULT_PARAMETERS = [
    'clOrdID',
    'symbol',
    'ordType',
    'side',
    'orderQty',
    'text'
]

PARAMETERS_BY_ORDER_TYPE_MAP = {
    'Market': {
        'params': [
            *DEFAULT_PARAMETERS
        ],
        'additional_params': {}
    },
    'Limit': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'price',
        ],
        'additional_params': {}
    },
}

BITMEX_CROSS_LEVERAGE_TYPE_PARAM = 0
