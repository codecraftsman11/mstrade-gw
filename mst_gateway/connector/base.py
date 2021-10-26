from abc import ABCMeta, abstractmethod
from ..logging import init_logger


class Connector(metaclass=ABCMeta):

    def __init__(self, auth=None, logger=None):
        self._auth = auth
        self._logger = logger or init_logger()
        self._handler = None

    @property
    def auth(self):
        return self._auth

    @property
    def handler(self):
        return self._handler

    @property
    def logger(self):
        return self._logger

    @abstractmethod
    def _connect(self, **kwargs):
        pass

    def open(self, **kwargs):
        self._handler = self._connect(**kwargs)
        return self._handler

    def close(self):
        pass

    def __str__(self):
        return self.__name__

    def __setstate__(self, state):
        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def __del__(self):
        self.close()
