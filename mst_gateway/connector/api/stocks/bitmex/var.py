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


ORDER_TYPE_AND_EXECUTION_READ_MAP = {
    'Market': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
    'Limit': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    'Stop': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
    'StopLimit': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
    'MarketIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
    'LimitIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
}


STORE_ORDER_TYPE_AND_EXECUTION_READ_MAP = {
    f'{api.OrderType.market}|{api.OrderExec.market}': 'Market',
    f'{api.OrderType.limit}|{api.OrderExec.limit}': 'Limit',
    f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'Stop',
    f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'StopLimit',
    f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'MarketIfTouched',
    f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'LimitIfTouched',
    # We currently map TS-MARKET to 'Stop', but it can also work with 'MarketIfTouched'
    f'{api.OrderType.trailing_stop}|{api.OrderExec.market}': 'Stop',
    # We currently map TS-LIMIT to 'StopLimit', but it can also work with 'LimitIfTouched':
    f'{api.OrderType.trailing_stop}|{api.OrderExec.limit}': 'StopLimit'

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
    # Market
    f'{api.OrderType.market}|{api.OrderExec.market}': {
        'params': [
            *DEFAULT_PARAMETERS
        ],
        'additional_params': {}
    },
    # Limit
    f'{api.OrderType.limit}|{api.OrderExec.limit}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'price',
        ],
        'additional_params': {}
    },
    # StopLimit
    f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'price',
            'stopPx'
        ],
        'additional_params': {}
    },
    # Stop
    f'{api.OrderType.stop_loss}|{api.OrderExec.market}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'stopPx'
        ],
        'additional_params': {}
    },
    # LimitIfTouched
    f'{api.OrderType.take_profit}|{api.OrderExec.limit}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'price',
            'stopPx',
        ],
        'additional_params': {}
    },
    # MarketIfTouched
    f'{api.OrderType.take_profit}|{api.OrderExec.market}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'stopPx'
        ],
        'additional_params': {}
    },
    # StopLimit and LimitIfTouched
    f'{api.OrderType.trailing_stop}|{api.OrderExec.limit}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'price',
            'stopPx',
            'pegOffsetValue'
        ],
        'additional_params': {
            'pegPriceType': 'TrailingStopPeg'
        }
    },
    # Stop and MarketIfTouched
    f'{api.OrderType.trailing_stop}|{api.OrderExec.market}': {
        'params': [
            *DEFAULT_PARAMETERS,
            'timeInForce',
            'execInst',
            'displayQty',
            'stopPx',
            'pegOffsetValue'
        ],
        'additional_params': {
            'pegPriceType': 'TrailingStopPeg'
        }
    }
}
