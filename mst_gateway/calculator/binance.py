import re
from typing import Optional, Tuple
from mst_gateway.calculator.base import FinFactory
from mst_gateway.connector import api


class BinanceFinFactory(FinFactory):

    @classmethod
    def get_contract_multiplier(cls, symbol: str) -> int:
        if re.match(r"^btcusd", symbol):
            return 100
        return 10

    @classmethod
    def _is_futures_coin(cls, **kwargs) -> bool:
        return kwargs.get('schema', '').lower() == api.OrderSchema.futures_coin

    @classmethod
    def calc_face_price(cls, symbol: str, price: float, **kwargs) -> Tuple[Optional[float], Optional[bool]]:
        if cls._is_futures_coin(**kwargs):
            try:
                return cls.get_contract_multiplier(symbol) / price, True
            except (TypeError, ZeroDivisionError):
                return None, None
        return price, False

    @classmethod
    def calc_price(cls, symbol: str, face_price: float, **kwargs) -> Optional[float]:
        if cls._is_futures_coin(**kwargs):
            try:
                return cls.get_contract_multiplier(symbol) / face_price
            except (TypeError, ZeroDivisionError):
                return None
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
            volume and leverage_brackets and
            None not in (entry_price, maint_margin, side, mark_price, position_margin, unrealised_pnl)
        ):
            notional_value = volume * mark_price
            maint_margin_rate, maint_amount = cls.filter_leverage_brackets(leverage_brackets, notional_value)
            if None not in (maint_margin_rate, maint_amount):
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
    def filter_leverage_brackets(cls, leverage_brackets: list, notional_value: float) -> tuple:
        maint_margin_rate = None
        maint_amount = None
        for lb in leverage_brackets:
            if lb['notionalFloor'] <= notional_value < lb['notionalCap']:
                maint_margin_rate = lb['maintMarginRatio']
                maint_amount = lb['cum']
        return maint_margin_rate, maint_amount

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
