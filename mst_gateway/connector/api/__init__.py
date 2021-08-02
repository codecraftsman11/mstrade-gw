# flake8: noqa
from importlib import import_module
from .types import *

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def init(params: dict, auth=None, cls=None, logger=None):
    cls = cls or get_rest_api_class('.stocks.bitmex')
    return cls(url=params.get('url', None), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        connector.open()
    return connector


def get_rest_api_class(path, **kwargs):
    return import_module(path, __package__).get_rest_api_class(**kwargs)


def get_ws_api_class(path, **kwargs):
    return import_module(path, __package__).get_ws_api_class(**kwargs)
