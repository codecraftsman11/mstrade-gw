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

BINANCE_LEVERAGE_TYPE_CROSS = "CROSSED"
BINANCE_LEVERAGE_TYPE_ISOLATED = "ISOLATED"
