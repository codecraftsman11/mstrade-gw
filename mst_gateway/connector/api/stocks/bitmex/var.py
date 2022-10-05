from mst_gateway.connector import api

BITMEX_THROTTLE_LIMITS = {
    'ws': 50,
    'rest': 100,
    'order': 10
}

BITMEX_MAX_QUOTE_BINS_COUNT = 750

BITMEX_BUY = "Buy"
BITMEX_SELL = "Sell"

BITMEX_ORDER_STATUS_NEW = 'New'
BITMEX_ORDER_DELETE_ACTION_STATUSES = ('Filled', 'Canceled', 'PendingCancel', 'Stopped', 'Rejected', 'Expired')

'''
See the FIX Spec for explanations of these fields. 
https://www.onixs.biz/fix-dictionary/5.0.SP2/msgType_D_68.html
https://www.onixs.biz/fix-dictionary/5.0.SP2/tagNum_39.html
https://www.onixs.biz/fix-dictionary/5.0.SP2/msgType_8_8.html
'''
BITMEX_ORDER_STATUS_MAP = {
    'PendingNew': api.OrderState.pending,
    'New': api.OrderState.pending,
    'PartiallyFilled': api.OrderState.active,
    'AcceptedForBidding': api.OrderState.pending,
    'Suspended': api.OrderState.pending,
    'DoneForDay': api.OrderState.pending,
    'PendingCancel': api.OrderState.pending,
    'PendingReplace': api.OrderState.pending,
    'Calculated': api.OrderState.closed,
    'Filled': api.OrderState.closed,
    'Stopped': api.OrderState.closed,
    'Canceled': api.OrderState.closed,
    'Rejected': api.OrderState.closed,
    'Expired': api.OrderState.expired,
}

BITMEX_ORDER_TTL_MAP = {
    'ImmediateOrCancel': api.OrderTTL.IOC,
    'FillOrKill': api.OrderTTL.FOK,
    'GoodTillCancel': api.OrderTTL.GTC
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
    'iceberg_volume': 'displayQty',
    'H1': 'GoodTillCancel',
    'H4': 'GoodTillCancel',
    'D1': 'GoodTillCancel',
    'GTC': 'GoodTillCancel',
    'FOK': 'FillOrKill',
    'IOC': 'ImmediateOrCancel',
    'reduce_only': 'ReduceOnly'
}

DEFAULT_PARAMETERS = [
    'clOrdID',
    'orderID',
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
            'ReduceOnly'
        ],
        'additional_params': {}
    },
    'Stop': {
        'params': [
            *DEFAULT_PARAMETERS,
            'stopPx',
            'execInst',
            'ReduceOnly'
        ],
        'additional_params': {}
    },
    'StopLimit': {
        'params': [
            *DEFAULT_PARAMETERS,
            'stopPx',
            'price',
            'execInst',
            'ReduceOnly'
        ],
        'additional_params': {}
    },
    'MarketIfTouched': {
        'params': [
            *DEFAULT_PARAMETERS,
            'stopPx',
            'execInst',
            'ReduceOnly'
        ],
        'additional_params': {}
    },
    'LimitIfTouched': {
        'params': [
            *DEFAULT_PARAMETERS,
            'stopPx',
            'price',
            'execInst',
            'ReduceOnly'
        ],
        'additional_params': {}
    },
    'TrailingStop': {
        'params': [
            *DEFAULT_PARAMETERS,
            'stopPx',
            'pegOffsetValue',
            'pegPriceType',
            'execInst',
            'ReduceOnly'
        ],
        'additional_params': {
            'pegPriceType': 'TrailingStopPeg',
            'execInst': 'LastPrice',
            'ordType': 'Stop'
        }
    }

}

BITMEX_CROSS_LEVERAGE_TYPE_PARAM = 0

BITMEX_VIP_LEVELS = [
    {'taker': 0.0005, 'type': 'VIP0'},
    {'taker': 0.0004, 'type': 'VIP1'},
    {'taker': 0.00035, 'type': 'VIP2'},
    {'taker': 0.0003, 'type': 'VIP3'},
    {'taker': 0.00025, 'type': 'VIP4'},
]

BITMEX_AVERAGE_DAILY_VOLUME = {
    'VIP0': 5_000_000,
    'VIP1': 5_000_000,
    'VIP2': 10_000_000,
    'VIP3': 25_000_000,
    'VIP4': 50_000_000
}
