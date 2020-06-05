from abc import abstractmethod
from typing import Optional, Tuple, Union, List
from logging import Logger
from ...base import Connector
from ..errors import ERROR_OK
from .. import (
    OrderType,
    BUY,
    SELL
)
from .throttle import ThrottleRest


class StockRestApi(Connector):
    throttle = ThrottleRest()
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._keepalive: bool = False
        self._compress: bool = False
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        super().__init__(auth, logger)

    @abstractmethod
    def ping(self) -> bool:
        raise NotImplementedError

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
    def get_wallet(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_symbol(self, symbol) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_symbols(self, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: str = OrderType.market,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[dict]:
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

    def list_order_book(
            self, symbol: str, depth: int = None, side: int = None,
            split: bool = False, offset: int = 0, schema: str = None) -> Union[list, dict]:
        if side is not None \
           and side not in (BUY, SELL):
            return [] if split else {BUY: [], SELL: []}
        return self.get_order_book(symbol, depth, side, split, offset, schema)

    @abstractmethod
    def list_trades(self, symbol, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_order_book(
            self, symbol: str, depth: int = None, side: int = None,
            split: bool = False, offset: int = 0, schema: str = None) -> Union[list, dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str,
                        amount: Union[float, str]) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_borrow_repay(self, action: str, schema: str, asset: str,
                            amount: Union[float, str]) -> Optional[dict]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        raise NotImplementedError
