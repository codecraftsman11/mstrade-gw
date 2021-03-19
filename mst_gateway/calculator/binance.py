from typing import Optional, Tuple
from mst_gateway.calculator import BitmexFinFactory


class BinanceFinFactory(BitmexFinFactory):

    @classmethod
    def filter_leverage_brackets(cls, leverage_brackets: list, notional_value: float) -> tuple:
        for lb in leverage_brackets:
            if lb['notionalFloor'] <= notional_value < lb['notionalCap']:
                return lb['maintMarginRatio'], lb['cum']
        return None, None

    @classmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
        return price, False

    @classmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        return face_price

    @classmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        abs_volume = kwargs.get('abs_volume')
        mark_price = kwargs.get('mark_price')
        wallet_balance = kwargs.get('wallet_balance')
        unrealised_pnl = kwargs.get('unrealised_pnl')
        leverage_brackets = kwargs.get('leverage_brackets')
        liquidation_price = None
        if (
            abs_volume is not None
            and mark_price is not None
            and wallet_balance is not None
            and unrealised_pnl is not None
            and leverage_brackets
        ):
            notional_value = abs_volume * mark_price
            maint_margin_rate, maint_amount = cls.filter_leverage_brackets(
                leverage_brackets, notional_value
            )
            if maint_margin_rate is not None and maint_amount is not None:
                liquidation_price = (
                    wallet_balance - maint_margin + unrealised_pnl + maint_amount -
                    direction * abs_volume * entry_price
                ) / (abs_volume * maint_margin_rate - direction * abs_volume)
        return liquidation_price

    @classmethod
    def calc_liquidation_cross_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        return cls.calc_liquidation_isolated_price(entry_price, maint_margin, direction, **kwargs)
