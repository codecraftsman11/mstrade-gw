from abc import ABCMeta, abstractmethod


class Connector(metaclass=ABCMeta):

    def __init__(self, auth=None, logger=None):
        self._auth = auth
        self._logger = logger
        self._handler = None

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()
