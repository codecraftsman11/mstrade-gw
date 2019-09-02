from abc import ABCMeta, abstractmethod
from logging import Logger
from ...base import Connector
from .. import MARKET
from ..errors import ERROR_OK
from ..utils.order_book import pad_order_book


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
        raise NotImplementedError

    @abstractmethod
    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def list_quote_bins(self, symbol, binsize='1m', count=100, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_symbols(self, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: int = MARKET,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_orders(self, symbol: str, active_only: bool = True,
                    count: int = None, offset: int = 0, options: dict = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def cancel_all_orders(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close_order(self, order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close_all_orders(self, symbol: str) -> bool:
        raise NotImplementedError

    def list_order_book(self, symbol: str, depth: int = None, tick_size: int = None) -> list:
        data = self._do_list_order_book(symbol, depth)
        if tick_size is None:
            return data
        if not data:
            return data
        start = data[0]['price']
        finish = data[-1]['price']
        steps = int((finish - start) / tick_size)
        if steps == depth * 2:
            return data
        return pad_order_book(data, tick_size)

    @abstractmethod
    def _do_list_order_book(self, symbol: str, depth: int = None) -> list:
        raise NotImplementedError
