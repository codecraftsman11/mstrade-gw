# pylint: disable=broad-except
from importlib import import_module
from datetime import datetime

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


def side_valid(value):
    try:
        return isinstance(value, int) and value in [SELL, BUY]
    except Exception:
        return False


def order_id_valid(value):
    try:
        return isinstance(value, str) and value
    except Exception:
        return False


def type_valid(value):
    try:
        return isinstance(value, int) and value in [MARKET, LIMIT, STOP,
                                                    STOPLIMIT, TP, TPLIMIT]
    except Exception:
        return False


def datetime_valid(value):
    if isinstance(value, datetime):
        return True
    try:
        datetime.strptime(value, DATETIME_FORMAT)
    except ValueError:
        return False
    return True
