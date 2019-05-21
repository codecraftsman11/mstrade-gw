from abc import ABCMeta, abstractmethod


class Connector(object):
    __metaclass__ = ABCMeta

    def __init__(self, auth=None, logger=None):
        self._auth = auth
        self._logger = logger
        self._handler = None

    @property
    def handler(self):
        return self._handler

    @abstractmethod
    def _connect(self, **kwargs):
        pass

    def open(self):
        self._handler = self._connect()
        return self._handler

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()
