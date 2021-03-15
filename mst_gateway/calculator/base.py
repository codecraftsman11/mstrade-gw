from abc import abstractmethod
from typing import (
    Union, Tuple, Optional
)


class FinFactory:

    @classmethod
    @abstractmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_liquidation_cross_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        raise NotImplementedError
