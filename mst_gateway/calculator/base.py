from abc import abstractmethod
from typing import Tuple, Optional


class FinFactory:

    @classmethod
    @abstractmethod
    def calc_face_price(cls, symbol: str, price: float, **kwargs) -> Tuple[Optional[float], Optional[bool]]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_price(cls, symbol: str, face_price: float, **kwargs) -> Optional[float]:
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
    def direction_by_side(cls, side: int) -> int:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def side_by_direction(cls, direction: int) -> int:
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
    def calc_mark_price(cls, volume: float, entry_price: float, unrealised_pnl: float) -> Optional[float]:
        try:
            return (entry_price * volume + unrealised_pnl) / volume
        except (TypeError, ZeroDivisionError):
            return None
