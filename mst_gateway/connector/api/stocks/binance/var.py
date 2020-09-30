from .... import api

BINANCE_MAX_QUOTE_BINS_COUNT = 1000

BINANCE_WALLET_TYPES = [
    api.OrderSchema.exchange,
    api.OrderSchema.margin2,
    api.OrderSchema.futures
]

BINANCE_ORDER_TYPE_AND_EXECUTION_MAP = {
    'LIMIT': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    'MARKET': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
    'STOP_LOSS': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
    'STOP_LOSS_LIMIT': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
    'TAKE_PROFIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
    'TAKE_PROFIT_LIMIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
    'LIMIT_MAKER': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    'STOP': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
    'STOP_MARKET': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
    'TAKE_PROFIT_MARKET': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
    'TRAILING_STOP_MARKET': {'type': api.OrderType.trailing_stop, 'execution': api.OrderExec.market},
}

BINANCE_ORDER_TYPE_AND_EXECUTION_PER_SCHEMA_MAP = {
    api.OrderSchema.margin2: {
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT',
        f'{api.OrderType.market}|{api.OrderExec.market}': 'MARKET',
        f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'STOP_LOSS',
        f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'STOP_LOSS_LIMIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'TAKE_PROFIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'TAKE_PROFIT_LIMIT',
        f'{api.OrderType.limit}|{api.OrderExec.market}': 'LIMIT_MAKER',
    },
    api.OrderSchema.exchange: {
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT',
        f'{api.OrderType.market}|{api.OrderExec.market}': 'MARKET',
        f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'STOP_LOSS',
        f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'STOP_LOSS_LIMIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'TAKE_PROFIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'TAKE_PROFIT_LIMIT',
        f'{api.OrderType.limit}|{api.OrderExec.market}': 'LIMIT_MAKER',
    },
    api.OrderSchema.futures: {
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT',
        f'{api.OrderType.market}|{api.OrderExec.market}': 'MARKET',
        f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'STOP',
        f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'STOP_MARKET',
        f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'TAKE_PROFIT_MARKET',
        f'{api.OrderType.trailing_stop}|{api.OrderExec.market}': 'TRAILING_STOP_MARKET',
    }
}

BINANCE_ORDER_SIDE_BUY = 'BUY'
BINANCE_ORDER_SIDE_SELL = 'SELL'

BINANCE_ORDER_STATUS_NEW = 'NEW'

BINANCE_ORDER_DELETE_ACTION_STATUSES = ('FILLED', 'CANCELED', 'EXPIRED', 'REJECTED')

BINANCE_EXECUTION_STATUS_MAP = {
    'PARTIALLY_FILLED': api.OrderState.active,
    BINANCE_ORDER_STATUS_NEW: api.OrderState.pending,
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

PARAMETERS_BY_ORDER_TYPE_MAP = {

    # GENERAL
    'LIMIT': {
        'price': ['price'],
        'ttl': ['ttl']
    },

    # SPOT/MARGIN
    'STOP_LOSS': {
        'stop_price': ['price']
    },
    'TAKE_PROFIT': {
        'stop_price': ['price']
    },
    'STOP_LOSS_LIMIT': {
        # Where is the stop price stored for our take_profit orders?
        'stop_price': ['price'],
        'price': ['price'],
        'ttl': ['ttl']
    },
    'TAKE_PROFIT_LIMIT': {
        # Where is the stop price stored for our take_profit orders?
        'stop_price': ['price'],
        'price': ['price'],
        'ttl': ['ttl']
    },

    # FUTURES
    'LIMIT_MAKER': {
        'price': ['price']
    },
    'STOP': {
        # Where is the stop price stored for our stop_loss orders?
        'stop_price': ['price'],
        'price': ['price']
    },
    'STOP_MARKET': {
        'stop_price': ['price']
    },
    'TAKE_PROFIT_MARKET': {
        'stop_price': ['price']
    },
    'TRAILING_STOP_MARKET': {
        # Where is the callback_rate stored for our trailing_stop orders?
        'callback_rate': ['compression', 'stop'],
        'price': ['price']
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