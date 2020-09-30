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
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT',
        f'{api.OrderType.market}|{api.OrderExec.market}': 'MARKET',
        f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'STOP_LOSS',
        f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'STOP_LOSS_LIMIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'TAKE_PROFIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'TAKE_PROFIT_LIMIT',
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT_MAKER',
    },
    api.OrderSchema.exchange: {
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT',
        f'{api.OrderType.market}|{api.OrderExec.market}': 'MARKET',
        f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'STOP_LOSS',
        f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'STOP_LOSS_LIMIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'TAKE_PROFIT',
        f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'TAKE_PROFIT_LIMIT',
        f'{api.OrderType.limit}|{api.OrderExec.limit}': 'LIMIT_MAKER',
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

BINANCE_PARAMETER_NAMES_MAP = {
    'exchange_order_id': 'orderId',
    'order_type': 'type',
    'volume': 'quantity',
    'iceberg_volume': 'icebergQty',
    'stop_price': 'stopPrice',
    'ttl': 'timeInForce',
}

PARAMETERS_BY_ORDER_TYPE_MAP = {

    # GENERAL
    'LIMIT': {
        'price': ['price'],
        'ttl': ['ttl']
    },

    # SPOT/MARGIN
    'STOP_LOSS': {
        'stop_price': ['cancel_price']
    },
    'TAKE_PROFIT': {
        'stop_price': ['cancel_price']
    },
    'STOP_LOSS_LIMIT': {
        'stop_price': ['cancel_price'],
        'price': ['price'],
        'ttl': ['ttl']
    },
    'TAKE_PROFIT_LIMIT': {
        'stop_price': ['cancel_price'],
        'price': ['price'],
        'ttl': ['ttl']
    },

    # FUTURES
    'LIMIT_MAKER': {
        'price': ['price']
    },
    'STOP': {
        'stop_price': ['cancel_price'],
        'price': ['price']
    },
    'STOP_MARKET': {
        'stopPx': ['cancel_price']
    },
    'TAKE_PROFIT_MARKET': {
        'stop_price': ['cancel_price']
    },
    'TRAILING_STOP_MARKET': {
        'callback_rate': ['compression', 'stop'],
        'price': ['price']
    }
}


EXTRA_PARAMETERS_MAP = {
    'is_iceberg': {
        'iceberg_volume': 'iceberg_volume'
    }
}