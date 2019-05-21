from abc import ABCMeta, abstractmethod
from logging import Logger
from ..base import Connector
from . import ERROR_OK


class StockApi(Connector):
    __metaclass__ = ABCMeta
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        super().__init__(auth, logger)

    @abstractmethod
    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        return None

    @abstractmethod
    def get_user(self, **kwargs) -> dict:
        return None

    @abstractmethod
    def list_symbols(self, **kwargs) -> list:
        return None

    @abstractmethod
    def create_order(self, symbol: str, order_type: int, rate: float,
                     quantity: float, options: dict = None) -> bool:
        pass
