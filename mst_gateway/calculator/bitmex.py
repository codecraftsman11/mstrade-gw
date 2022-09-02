from typing import Optional, Union
from mst_gateway.calculator import FinFactory
from mst_gateway.connector import api


class BitmexFinFactory(FinFactory):

    @classmethod
    def direction_by_side(cls, side: int) -> int:
        if side == api.BUY:
            return -1
        return 1

    @classmethod
    def calc_liquidation_price(cls, side: int, volume: float, entry_price: float, leverage_type: str,
                               wallet_balance: float, **kwargs) -> Optional[float]:
        liquidation_price = None
        direction = cls.direction_by_side(side)
        taker_fee = kwargs.get('taker_fee')
        funding_rate = kwargs.get('funding_rate')
        maint_margin = kwargs.get('maint_margin')
        leverage = kwargs.get('leverage')
        try:
            leverage_type = leverage_type.lower()
            if leverage_type == api.LeverageType.isolated:
                liquidation_price = round(
                    entry_price / (
                        1 + (-direction * ((100 / leverage / 100) + 2 * taker_fee / 100)) +
                        (direction * (maint_margin + taker_fee + funding_rate) / 100)
                    ), 8)
            if leverage_type == api.LeverageType.cross:
                quantity = abs(volume)
                liquidation_price = round(
                    (direction * quantity * entry_price) / (
                        (-wallet_balance * entry_price) +
                        ((maint_margin + taker_fee + funding_rate) / 100 * quantity) +
                        (direction * quantity)
                    ), 8)
        except (TypeError, ZeroDivisionError):
            pass
        if liquidation_price is not None and liquidation_price < 0:
            liquidation_price = None
        return liquidation_price

    @classmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(quantity / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def calc_face_price(cls, price: float, **kwargs) -> Optional[float]:
        face_price = None
        if not kwargs:
            return face_price
        is_quanto = kwargs.get('is_quanto')
        is_inverse = kwargs.get('is_inverse')
        multiplier = kwargs.get('multiplier')
        underlying_multiplier = kwargs.get('underlying_multiplier')
        try:
            if is_quanto:
                face_price = multiplier / 100_000_000 * price
            elif is_inverse:
                face_price = 1 / price
            elif not is_quanto and not is_inverse and underlying_multiplier:
                face_price = price / underlying_multiplier
            return round(face_price, 8)
        except (TypeError, ZeroDivisionError):
            return None

    @classmethod
    def calc_price(cls, face_price: float, **kwargs) -> Optional[float]:
        if not kwargs:
            return None
        is_quanto = kwargs.get('is_quanto')
        is_inverse = kwargs.get('is_inverse')
        multiplier = kwargs.get('multiplier', 1)
        underlying_multiplier = kwargs.get('underlying_multiplier', 1)
        try:
            if is_quanto:
                face_price = 100_000_000 * face_price / multiplier
            elif is_inverse:
                face_price = 1 / face_price
            else:
                face_price = face_price * underlying_multiplier
        except (TypeError, ZeroDivisionError):
            return None
        return round(face_price, 8)

    @classmethod
    def side_by_direction(cls, direction: int) -> int:
        if direction == 1:
            return api.SELL
        return api.BUY
