from abc import ABCMeta, abstractmethod
from logging import Logger
from ...base import Connector
from .. import ERROR_OK, MARKET


class StockRestApi(Connector):
    __metaclass__ = ABCMeta
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._keepalive: bool = None
        self._compress: bool = None
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        super().__init__(auth, logger)

    @abstractmethod
    def get_quote(self, symbol, timeframe=None, **kwargs) -> dict:
        pass

    @abstractmethod
    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        pass

    @abstractmethod
    def list_quote_bins(self, symbol, binsize='1m', count=100, **kwargs) -> list:
        pass

    @abstractmethod
    def get_user(self, **kwargs) -> dict:
        pass

    @abstractmethod
    def list_symbols(self, **kwargs) -> list:
        pass

    @abstractmethod
    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: int = MARKET,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    def get_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    def list_orders(self, symbol: str, active_only: bool = True, options: dict = None) -> list:
        pass

    @abstractmethod
    def cancel_all_orders(self) -> bool:
        pass

    @abstractmethod
    def close_order(self, order_id: str) -> bool:
        pass

    @abstractmethod
    def close_all_orders(self, symbol: str) -> bool:
        pass
