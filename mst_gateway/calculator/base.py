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
    def calc_liquidation_isolated_price(cls, entry_price: float, leverage: float, maint_margin: float,
                                        taker_fee: float, funding_rate: float, position: str = 'short'):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_liquidation_cross_price(cls, quantity: Union[int, float], entry_price: float, margin_balance: float,
                                     maint_margin: float, taker_fee: float, funding_rate: float,
                                     position: str = 'short'):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        raise NotImplementedError

    @classmethod
    def calc_unrealised_pnl(cls, volume: Union[int, float], entry_price: float,
                            mark_price: float, side: int) -> Optional[float]:
        try:
            if side:
                return (entry_price - mark_price) * volume
            return (mark_price - entry_price) * volume
        except TypeError:
            return None
