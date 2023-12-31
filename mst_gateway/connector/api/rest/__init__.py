from hashlib import sha256
from time import time
from abc import abstractmethod
from typing import Optional, Union
from logging import Logger
from ...base import Connector
from mst_gateway.storage import StateStorage
from mst_gateway.calculator import FinFactory
from ..errors import ERROR_OK
from .. import OrderType, BUY, SELL, PositionSide, BaseOrderTypeConverter
from .throttle import ThrottleRest
from mst_gateway.exceptions import RecoverableError


class StockRestApi(Connector):
    driver = 'base'
    name = 'Base'
    throttle = ThrottleRest()
    storage = StateStorage()
    fin_factory = FinFactory()
    order_converter = BaseOrderTypeConverter()

    def __init__(self, name: str = None, auth: dict = None, test: bool = True, logger: Logger = None,
                 state_storage=None, ratelimit=None):
        if name is not None:
            self.name = name.lower()
        self.test = test
        self._keepalive: bool = False
        self._compress: bool = False
        self._error: tuple = ERROR_OK
        if state_storage is not None:
            self.storage = StateStorage(storage=state_storage)
        self.ratelimit = ratelimit
        super().__init__(auth, logger)

    def throttle_hash_name(self, **kwargs):
        if self.auth:
            return sha256(str(self.auth.get('api_key', '')).encode('utf-8')).hexdigest()
        return super().throttle_hash_name(**kwargs)

    def validate_throttling(self, hash_name: str):
        reset_time = self.throttle.validate(hash_name, self.throttle.rest_limit)
        if reset_time:
            raise RecoverableError(
                f"Request was throttled. Expected available in {reset_time - int(time())} seconds."
            )

    @abstractmethod
    def ping(self, schema: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_quote_bins(self, symbol, schema: str, binsize='1m', count=100, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_user(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_api_key_permissions(self, schemas: list,  **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet(self, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_extra_data(self, schema: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_wallet_detail_extra_data(self, schema: str, asset: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_symbol(self, symbol, schema) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_symbols(self, schema, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_exchange_symbol_info(self, schema: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, symbol: str, schema: str, side: int, volume: float, order_type: str = OrderType.market,
                     price: float = None, options: dict = None, position_side: str = PositionSide.both,
                     order_id: str = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def update_order(self, symbol: str, schema: str, side: int, volume: float, order_type: str = OrderType.market,
                     price: float = None, options: dict = None, position_side: str = PositionSide.both,
                     order_id: str = None, new_order_id: str = None, exchange_order_id: str = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, symbol: str, schema: str, order_id: str = None, exchange_order_id: str = None) -> dict:
        """
        Cancel active order (limit, etc...)
        """
        raise NotImplementedError

    @abstractmethod
    def get_order(self, symbol: str, schema: str, order_id: str = None,
                  exchange_order_id: str = None) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def list_orders(self, schema: str, symbol: str = None, active_only: bool = True,
                    count: int = None, offset: int = 0) -> list:
        raise NotImplementedError

    @abstractmethod
    def cancel_all_orders(self, schema: str) -> bool:
        """
        Cancel all active orders (limit, etc...)
        """
        raise NotImplementedError

    @abstractmethod
    def close_order(self, symbol: str, schema: str, order_id: str = None, exchange_order_id: str = None) -> bool:
        """
        Close position
        """
        raise NotImplementedError

    @abstractmethod
    def close_all_orders(self, symbol: str, schema: str) -> bool:
        """
        Close all positions
        """
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
                        amount: Union[float, str], symbol: str = None) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_borrow(self, schema: str, asset: str, amount: Union[float, str], **kwargs) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def wallet_repay(self, schema: str, asset: str, amount: Union[float, str], **kwargs) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    def currency_exchange_symbols(self, schema: str, symbol: str = None) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_symbols_currencies(self, schema: str) -> dict:
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
    def get_funding_rates(self, symbol: str, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        raise NotImplementedError

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

    @abstractmethod
    def get_position_mode(self, schema: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def change_position_mode(self, schema: str, mode: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_position(self, schema: str, symbol: str,  position_side: str = PositionSide.both, **kwargs) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_positions(self, schema: str, **kwargs) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_positions_state(self, schema: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_liquidation(
        self,
        symbol: str,
        schema: str,
        leverage_type: str,
        wallet_balance: float,
        side: int,
        volume: float,
        price: float,
        **kwargs,
    ) -> dict:
        raise NotImplementedError

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        self.storage.storage = {}
        self.throttle.storage = {}
        self.ratelimit = None
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
