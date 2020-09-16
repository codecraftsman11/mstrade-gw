from .... import api


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


BITMEX_BUY = "Buy"
BITMEX_SELL = "Sell"


BITMEX_EXECUTION_STATUS_MAP = {
    'PartiallyFilled': api.OrderState.active,
    'New': api.OrderState.pending,
    'Filled': api.OrderState.closed,
    'Canceled': api.OrderState.closed,
}
