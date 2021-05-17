from typing import Optional, Tuple, Union
from mst_gateway.calculator.base import FinFactory


class BinanceFinFactory(FinFactory):

    @classmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float], Optional[bool]]:
        return price, False

    @classmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        return face_price

    @classmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, maint_margin: float, side: int, **kwargs):
        liquidation_price = None
        volume = abs(kwargs.get('volume'))
        mark_price = kwargs.get('mark_price')
        position_margin = kwargs.get('position_margin')
        unrealised_pnl = kwargs.get('unrealised_pnl')
        leverage_brackets = kwargs.get('leverage_brackets')
        if (
            volume
            and mark_price is not None
            and position_margin is not None
            and unrealised_pnl is not None
            and leverage_brackets
        ):
            notional_value = volume * mark_price
            maint_margin_rate, maint_amount = cls.filter_leverage_brackets(leverage_brackets, notional_value)
            if maint_margin_rate is not None and maint_amount is not None:
                direction = cls.direction_by_side(side)
                liquidation_price = (
                    position_margin - maint_margin + unrealised_pnl + maint_amount -
                    direction * volume * entry_price
                ) / (volume * maint_margin_rate - direction * volume)
        if liquidation_price is not None and liquidation_price < 0:
            liquidation_price = None
        return liquidation_price

    @classmethod
    def calc_liquidation_cross_price(cls, entry_price: float, maint_margin: float, side: int, **kwargs):
        return cls.calc_liquidation_isolated_price(entry_price, maint_margin, side, **kwargs)

    @classmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(quantity / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def filter_leverage_brackets(cls, leverage_brackets: list, notional_value: float) -> tuple:
        maint_margin_rate = None
        maint_amount = None
        for lb in leverage_brackets:
            if lb['notionalFloor'] <= notional_value < lb['notionalCap']:
                maint_margin_rate = lb['maintMarginRatio']
                maint_amount = lb['cum']
        return maint_margin_rate, maint_amount
