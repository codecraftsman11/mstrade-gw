import re
from typing import Optional, Tuple, Union
from mst_gateway.calculator import FinFactory
from mst_gateway.connector import api


class BitmexFinFactory(FinFactory):

    @classmethod
    def direction_by_side(cls, side: int) -> int:
        if side == api.BUY:
            return -1
        return 1

    @classmethod
    def calc_liquidation_price(
        cls, side: int, leverage_type: str, entry_price: float, **kwargs
    ) -> Optional[float]:
        taker_fee = kwargs.get('taker_fee')
        funding_rate = kwargs.get('funding_rate')
        maint_margin = kwargs.get('maint_margin')
        try:
            liquidation_price = None
            direction = cls.direction_by_side(side)
            leverage_type = leverage_type.lower()
            if leverage_type == api.LeverageType.isolated:
                liquidation_price = round(
                    entry_price / (
                        1 + (-direction * ((100 / kwargs.get('leverage') / 100) + 2 * taker_fee / 100)) +
                        (direction * (maint_margin + taker_fee + funding_rate) / 100)
                    ), 8)
            if leverage_type == api.LeverageType.cross:
                quantity = abs(kwargs.get('volume'))
                liquidation_price = round(
                    (direction * quantity * entry_price) / (
                        (-kwargs.get('wallet_balance') * entry_price) +
                        ((maint_margin + taker_fee + funding_rate) / 100 * quantity) +
                        (direction * quantity)
                    ), 8)
        except (TypeError, ZeroDivisionError):
            liquidation_price = None
        if liquidation_price is not None and liquidation_price < 0:
            liquidation_price = None
        return liquidation_price

    @classmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(quantity / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def calc_face_price(cls, symbol: str, price: float, **kwargs) -> Tuple[Optional[float], Optional[bool]]:
        _symbol = symbol.lower()
        result = (None, None)
        try:
            if re.match(r"^xbtusd(t)?$", _symbol):
                result = (1 / price, True)
            elif re.match(r"^xbt[fghjkmnquvxz]\d{2}$", _symbol):
                result = (1 / price, True)
            elif _symbol == "xbtjpy":
                result = (100 / price, True)
            elif _symbol == "xbtkrw":
                result = (1000 / price, True)
            elif _symbol in ("xbt7d_u105", "xbt7d_d95"):
                result = (0.1 * price, False)
            elif re.match(r"^adausd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = (0.01 * price, False)
            elif re.match(r"^(eth|bch)usd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = (1e-6 * price, False)
            elif re.match(r"^yfiusd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = (1e-7 * price, False)
            elif re.match(r"^ltcusd(t)?$", _symbol):
                result = (2e-6 * price, False)
            elif re.match(r"^uniusd(t)?$", _symbol):
                result = (1e-5 * price, False)
            elif re.match(r"^dogeusd(t)?$", _symbol):
                result = (0.001 * price, False)
            elif re.match(r"^(bnb|dot|eos|link|xtz)usd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = (0.0001 * price, False)
            elif re.match(r"^xrpusd(t)?$", _symbol):
                result = (0.0002 * price, False)
            elif re.match(r"^(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}$", _symbol):
                result = (price, False)
            elif re.match(r"^\w*xbt$", _symbol):
                result = (price, False)
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return result

    @classmethod
    def calc_price(cls, symbol: str, face_price: float, **kwargs) -> Optional[float]:
        _symbol = symbol.lower()
        result = None
        try:
            if re.match(r"^xbtusd(t)?$", _symbol):
                result = 1 / face_price
            elif re.match(r"^xbt[fghjkmnquvxz]\d{2}$", _symbol):
                result = 1 / face_price
            elif _symbol == "xbtjpy":
                result = 100 / face_price
            elif _symbol == "xbtkrw":
                result = 1000 / face_price
            elif _symbol in ("xbt7d_u105", "xbt7d_d95"):
                result = face_price / 0.1
            elif re.match(r"^adausd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = face_price / 0.01
            elif re.match(r"^(eth|bch)usd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = face_price / 1e-6
            elif re.match(r"^yfiusd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = face_price / 1e-7
            elif re.match(r"^ltcusd(t)?$", _symbol):
                result = face_price / 2e-6
            elif re.match(r"^uniusd(t)?$", _symbol):
                result = face_price / 1e-5
            elif re.match(r"^dogeusd(t)?$", _symbol):
                result = face_price / 0.001
            elif re.match(r"^(bnb|dot|eos|link|xtz)usd(t)?([fghjkmnquvxz]\d{2})?$", _symbol):
                result = face_price / 0.0001
            elif re.match(r"^xrpusd(t)?$", _symbol):
                result = face_price / 0.0002
            elif re.match(r"^(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}$", _symbol):
                result = face_price
            elif re.match(r"^\w*xbt$", _symbol):
                result = face_price
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return result

    @classmethod
    def side_by_direction(cls, direction: int) -> int:
        if direction == 1:
            return api.SELL
        return api.BUY
