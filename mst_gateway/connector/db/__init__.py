# flake8: noqa
from importlib import import_module
from .base import Connector
from .. import get_connector_class


def init(params, auth=None, cls=None, logger=None):
    cls = cls or get_connector_class('.db.mysql')
    return cls(host=params.get('host'), dbname=params.get('dbname'),
               port=params.get('port'), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        connector.open()
    return connector
