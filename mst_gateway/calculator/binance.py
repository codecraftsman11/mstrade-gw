from . import BitmexFinFactory
from typing import (
    Tuple, Optional
)


class BinanceFinFactory(BitmexFinFactory):

    @classmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
        return price, False

    @classmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        return face_price
