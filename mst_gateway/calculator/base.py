from abc import abstractmethod
from typing import Optional, Tuple, Union


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
    def calc_liquidation_price(cls, side: int, leverage_type: str, entry_price: float, **kwargs) -> Optional[float]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
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
    def calc_unrealised_pnl_by_side(cls, entry_price: float, mark_price: float, volume: float, side: int,
                                    **kwargs) -> Optional[float]:
        try:
            return (mark_price - entry_price) * cls.direction_by_side(side) * abs(volume)
        except TypeError:
            return None

    @classmethod
    def calc_unrealised_pnl_by_direction(cls, entry_price: float, mark_price: float, volume: float, direction: int,
                                         **kwargs) -> Optional[float]:
        try:
            return (mark_price - entry_price) * direction * abs(volume)
        except TypeError:
            return None

    @classmethod
    def calc_mark_price(cls, volume: float, entry_price: float, unrealised_pnl: float, **kwargs) -> Optional[float]:
        try:
            return (entry_price * volume + unrealised_pnl) / volume
        except (TypeError, ZeroDivisionError):
            return None

    @classmethod
    def calc_money_management(cls, face_price: float, volume: float, balance: float,
                              commission: float) -> Tuple[float, Optional[float]]:
        try:
            used = face_price * volume
            if commission:
                used *= abs(commission)
            return used, used / balance
        except (TypeError, ZeroDivisionError):
            return 0, None

