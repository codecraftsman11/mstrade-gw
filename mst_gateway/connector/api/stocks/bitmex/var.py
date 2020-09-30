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
}


STORE_ORDER_TYPE_AND_EXECUTION_READ_MAP = {
    f'{api.OrderType.market}|{api.OrderExec.market}': ORDER_TYPE_WRITE_MAP[api.OrderType.market],
    f'{api.OrderType.limit}|{api.OrderExec.limit}': ORDER_TYPE_WRITE_MAP[api.OrderType.limit],
}


BITMEX_BUY = "Buy"
BITMEX_SELL = "Sell"


BITMEX_PARAMETER_NAMES_MAP = {
    'order_id': 'clOrdID',
    'stopPx': 'stop_price',
    'volume': 'orderQty',
    'comments': 'text',
    'ttl': 'timeInForce',
    'ttl_type': 'timeInForce',
    'display_value': 'displayQty',
    'order_type': 'ordType',
    'is_passive': 'execInst',
    'iceberg_volume': 'displayQty'
}

BITMEX_UPDATE_PARAMETER_NAMES_MAP = {
    'order_id': 'origClOrdID'
}

PARAMETERS_BY_ORDER_TYPE_MAP = {
    'Limit': {
        'price': ['price'],
        'ttl': ['ttl']
    }
}

EXTRA_PARAMETERS_MAP = {
    'is_iceberg': {
        'iceberg_volume': 'iceberg_volume'
    },
    'is_passive': {
        'is_passive': 'is_passive'
    }
}