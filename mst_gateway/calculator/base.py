from abc import abstractmethod
from typing import (
    Union, Tuple, Optional
)
from mst_gateway.connector import api


class FinFactory:

    @classmethod
    @abstractmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float], Optional[bool]]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, maint_margin: float, side: int, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_liquidation_cross_price(cls, entry_price: float, maint_margin: float, side: int, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        raise NotImplementedError

    @classmethod
    def calc_unrealised_pnl_by_side(cls, entry_price: float, mark_price: float, volume: float,
                                    side: int) -> Optional[float]:
        if None in (entry_price, mark_price, volume, side):
            return None
        return (mark_price - entry_price) * cls.direction_by_side(side) * abs(volume)

    @classmethod
    def calc_unrealised_pnl_by_direction(cls, entry_price: float, mark_price: float, volume: float,
                                         direction: int) -> Optional[float]:
        if None in (entry_price, mark_price, volume, direction):
            return None
        return (mark_price - entry_price) * direction * abs(volume)

    @classmethod
    def direction_by_side(cls, side: int) -> int:
        if side == api.BUY:
            return 1
        return -1

    @classmethod
    def side_by_direction(cls, direction: int) -> int:
        if direction == 1:
            return api.BUY
        return api.SELL

    @classmethod
    def calc_mark_price(cls, volume: float, entry_price: float, unrealised_pnl: float):
        try:
            return (entry_price * volume + unrealised_pnl) / volume
        except (ValueError, ZeroDivisionError):
            return 0
