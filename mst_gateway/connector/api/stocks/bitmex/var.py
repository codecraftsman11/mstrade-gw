from .... import api

BITMEX_MAX_QUOTE_BINS_COUNT = 750


ORDER_TYPE_WRITE_MAP = {
    api.OrderType.market: 'Market',
    api.OrderType.limit: 'Limit',
    api.OrderType.sl_market: 'Stop',
    api.OrderType.sl_limit: 'StopLimit',
    api.OrderType.tp_market: 'MarketIfTouched',
    api.OrderType.tp_limit: 'LimitIfTouched'
}


ORDER_TYPE_READ_MAP = {
    v: k for k, v in ORDER_TYPE_WRITE_MAP.items()
}
