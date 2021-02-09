from abc import abstractmethod
from typing import Optional, Union
from logging import Logger
from ...base import Connector
from mst_gateway.storage import StateStorage
from mst_gateway.calculator import FinFactory
from ..errors import ERROR_OK
from .. import (
    OrderType,
    BUY,
    SELL
)
from .throttle import ThrottleRest


class StockRestApi(Connector):
    throttle = ThrottleRest()
    storage = StateStorage()
    fin_factory = FinFactory()
    BASE_URL = None
    name = 'Base'

    def __init__(self, name: str = None, url: str = None, auth: dict = None, logger: Logger = None,
                 throttle_storage=None, state_storage=None):
        if name is not None:
            self.name = name.lower()
        self._keepalive: bool = False
        self._compress: bool = False
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        if throttle_storage is not None:
            self.throttle = ThrottleRest(storage=throttle_storage)
        if state_storage is not None:
            self.storage = StateStorage(storage=state_storage)
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
    def list_quote_bins(self, symbol, schema: str, binsize='1m', count=100, **kwargs) -> list:
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
    def get_asset_balance(self, schema: str, asset: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_symbol(self, symbol, schema) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_symbols(self, schema, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_exchange_symbol_info(self) -> list:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, symbol: str, schema: str, side: int, volume: float,
                     order_type: str = OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def update_order(self, exchange_order_id: str, symbol: str,
                     schema: str, side: int, volume: float,
                     order_type: str = OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, exchange_order_id: str, symbol: str,
                     schema: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, exchange_order_id: str, symbol: str,
                  schema: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_orders(self, schema: str, symbol: str, active_only: bool = True,
                    count: int = None, offset: int = 0, options: dict = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def cancel_all_orders(self, schema: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close_order(self, exchange_order_id: str, symbol: str, schema: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close_all_orders(self, symbol: str, schema: str) -> bool:
        raise NotImplementedError

    def list_order_book(
        self,
        symbol: str,
        depth: int = None,
        side: int = None,
        split: bool = False,
        offset: int = 0,
        schema: str = None,
        min_volume_buy: float = None,
        min_volume_sell: float = None,
    ) -> Union[list, dict]:
        if side is not None \
           and side not in (BUY, SELL):
            return [] if split else {BUY: [], SELL: []}
        return self.get_order_book(
            symbol, depth, side, split, offset, schema, min_volume_buy, min_volume_sell,
        )

    @abstractmethod
    def list_trades(self, symbol: str, schema: str, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_order_book(
        self,
        symbol: str,
        depth: int = None,
        side: int = None,
        split: bool = False,
        offset: int = 0,
        schema: str = None,
        min_volume_buy: float = None,
        min_volume_sell: float = None,
    ) -> Union[list, dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str,
                        amount: Union[float, str]) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_borrow(self, schema: str, asset: str, amount: Union[float, str]) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_repay(self, schema: str, asset: str, amount: Union[float, str]) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def currency_exchange_symbols(self, schema: str, symbol: str = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_symbols_currencies(self, schema: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_summary(self, schemas: iter, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_order_commissions(self, schema: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_vip_level(self, schema: str) -> str:
        raise NotImplementedError

    def get_alt_currency_commission(self, schema: str) -> dict:
        return {
            'is_active': False,
            'currency': None
        }

    @abstractmethod
    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        raise NotImplementedError

    @abstractmethod
    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        raise NotImplementedError

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
