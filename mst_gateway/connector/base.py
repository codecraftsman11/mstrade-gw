from abc import ABCMeta, abstractmethod


class Connector(object):
    __metaclass__ = ABCMeta

    def __init__(self, auth=None, logger=None):
        self._auth = auth
        self._logger = logger
        self._handler = None

    @abstractmethod
    def _connect(self, **kwargs):
        pass

    def open(self):
        self._handler = self._connect()
        return self._handler

    def close(self):
        pass

    @property
    def handler(self):
        return self._handler
