from logging import Logger
from importlib import import_module
from .base import Connector
from ..exceptions import ConnectorError


def init(connector_type: str, params: dict, auth: dict = None, cls: type = None,
         logger: Logger = None) -> Connector:
    c_module = module(connector_type)
    return c_module.init(cls=cls, params=params, auth=auth, logger=logger)


def connect(connector_type: str, params: dict, auth: dict, cls: type = None,
            logger: Logger = None, **kwargs: any) -> Connector:
    c_module = module(connector_type)
    return c_module.connect(cls=cls, params=params,
                            auth=auth, logger=logger, **kwargs)


def module(connector_type=None):
    try:
        return import_module('.' + connector_type, __package__)
    except Exception:
        raise ConnectorError('Invalid connector type (%s)' % (connector_type))


def get_connector_class(path):
    return import_module(path, __package__).get_connector_class()
