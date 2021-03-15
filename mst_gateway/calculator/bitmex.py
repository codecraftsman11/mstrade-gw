import re
from typing import Union, Tuple, Optional
from mst_gateway.calculator import FinFactory


class BitmexFinFactory(FinFactory):

    @classmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        leverage = kwargs.get('leverage')
        taker_fee = kwargs.get('taker_fee')
        funding_rate = kwargs.get('funding_rate')
        result = None
        if leverage is not None and taker_fee is not None and funding_rate is not None:
            result = round(
                entry_price / (
                        1 +
                        (-direction * ((100 / leverage / 100) + 2 * taker_fee / 100)) +
                        (direction * (maint_margin + taker_fee + funding_rate) / 100)
                ), 8)
        return result

    @classmethod
    def calc_liquidation_cross_price(cls, entry_price: float, maint_margin: float, direction: int, **kwargs):
        quantity = kwargs.get('quantity')
        margin_balance = kwargs.get('margin_balance')
        taker_fee = kwargs.get('taker_fee')
        funding_rate = kwargs.get('funding_rate')
        result = None
        if quantity is not None and margin_balance is not None and taker_fee is not None and funding_rate is not None:
            result = round(
                (direction * quantity * entry_price) / (
                    (-margin_balance * entry_price) +
                    ((maint_margin + taker_fee + funding_rate) / 100 * quantity) +
                    (direction * quantity)
                ), 8)
        return result

    @classmethod
    def calc_leverage_level(cls, quantity: Union[int, float], entry_price: float, wallet_balance: float,
                            liquidation_price: float = None):
        result = round(quantity / (wallet_balance * 100 * entry_price) * 100**2, 8)
        return result

    @classmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
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
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
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
