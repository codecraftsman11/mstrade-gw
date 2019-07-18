# pylint: disable=broad-except
from importlib import import_module

# Sides
BUY = 0
SELL = 1

# Orders
MARKET = 0
LIMIT = 1
STOP = 2
STOPLIMIT = 3  # stop with discount to stock
TP = 4  # aka TakeProfit
TPLIMIT = 5  # aka limit TakeProfit

# Stop-loss
SL_MARKET = 0
SL_LIMIT = 1

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def init(params: dict, auth=None, cls=None, logger=None):
    cls = cls or import_module('.stocks.bitmex.rest',
                               package=__package__).BitmexRestApi
    return cls(url=params.get('url', None), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        return connector.connect()
    return connector
