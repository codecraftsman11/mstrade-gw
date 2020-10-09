from mst_gateway.connector import api


BITMEX_MAX_QUOTE_BINS_COUNT = 750


ORDER_TYPE_WRITE_MAP = {
    api.OrderType.market: 'Market',
    api.OrderType.limit: 'Limit',
}


ORDER_CLOSE_TYPE_MAP = {
    api.OrderType.stop_loss: 'Stop',
    api.OrderType.take_profit: 'MarketIfTouched',
}


ORDER_TYPE_READ_MAP = {
    v: k for k, v in ORDER_TYPE_WRITE_MAP.items()
}

# TODO: If the new order type mapping is approved, we can remove this variable and change the related functions
ORDER_TYPE_AND_EXECUTION_READ_MAP = {
    'Market': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
    'Limit': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    'Stop': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
    'StopLimit': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
    'MarketIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
    'LimitIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
}

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

UPDATED_PARAMETER_NAMES_MAP = {
    'order_id': 'origClOrdID'
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
