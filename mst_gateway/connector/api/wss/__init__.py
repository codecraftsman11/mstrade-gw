from typing import Dict
from abc import ABCMeta, abstractmethod
from logging import Logger
from ...base import Connector
from .. import ERROR_OK
from .channel import StockWssChannel


class StockWssConnector(Connector):
    __metaclass__ = ABCMeta
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        self._channels: Dict[str, StockWssChannel]
        super().__init__(auth, logger)

    @abstractmethod
    def subscirbe(self, channel: str, key: str, wss_channel: StockWssChannel):
        pass

    @abstractmethod
    def unsubscribe(self, channel: str, key: str):
        pass
