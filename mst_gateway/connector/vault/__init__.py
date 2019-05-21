from .base import Connector
from .exceptions import VaultError


__all__ = [
    'connect',
    'Connector',
    'VaultError'
]


def init(params, auth=None, cls=None, logger=None):
    if cls is None:
        from .hvac import Hvac
        cls = Hvac
    return cls(url=params.get('url'), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        return connector.connect()
    return connector
