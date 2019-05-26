from ... import api

BITMEX_MAX_QUOTE_BINS_COUNT = 750


ORDER_TYPE_WRITE_MAP = {
    api.MARKET: 'Market',
    api.LIMIT: 'Limit',
    api.STOP: 'Stop',
    api.STOPLIMIT: 'StopLimit',
    api.TP: 'MarketIfTouched',
    api.TPLIMIT: 'LimitIfTouched'
}


ORDER_TYPE_READ_MAP = {
    v: k for k, v in ORDER_TYPE_WRITE_MAP.items()
}
