# flake8: noqa
from importlib import import_module
from .types.order import (
    OrderType,
    OrderSchema,
    OrderState,
    ALGORITHM_ORDER_TYPES,
    BUY,
    SELL
)


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
DATETIME_OUT_FORMAT = "%Y-%m-%d %H:%M:%S.%fZ"


def init(params: dict, auth=None, cls=None, logger=None):
    cls = cls or get_rest_api_class('.stocks.bitmex')
    return cls(url=params.get('url', None), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        return connector.connect()
    return connector

def get_rest_api_class(path):
    return import_module(path).get_rest_api()

def get_ws_api_class(path):
    return import_module(path).get_ws_api()
