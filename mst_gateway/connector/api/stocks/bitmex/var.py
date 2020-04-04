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
