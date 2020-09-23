from .... import api

BINANCE_MAX_QUOTE_BINS_COUNT = 1000

BINANCE_WALLET_TYPES = [
    'exchange',
    'margin2',
    'futures'
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
        'LIMIT': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
        'MARKET': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
        'STOP_LOSS': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
        'STOP_LOSS_LIMIT': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
        'TAKE_PROFIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
        'TAKE_PROFIT_LIMIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
        'LIMIT_MAKER': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    },
    api.OrderSchema.exchange: {
        'LIMIT': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
        'MARKET': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
        'STOP_LOSS': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
        'STOP_LOSS_LIMIT': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
        'TAKE_PROFIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
        'TAKE_PROFIT_LIMIT': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
        'LIMIT_MAKER': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
    },
    api.OrderSchema.futures: {
        'LIMIT': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
        'MARKET': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
        'STOP': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
        'STOP_MARKET': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
        'TAKE_PROFIT_MARKET': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
        'TRAILING_STOP_MARKET': {'type': api.OrderType.trailing_stop, 'execution': api.OrderExec.market},
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

BINANCE_PARAMETER_NAMES_MAP = {
    'order_id': 'newClientOrderId',
    'exchange_order_id': 'orderId',
    'volume': 'quantity',
    'iceberg_volume': 'icebergQty',
    'stop_price': 'stopPrice',
    'ttl': 'timeInForce',
}
