import re
from . import FinFactory
from typing import (
    Union, Tuple, Optional
)


class BitmexFinFactory(FinFactory):

    @classmethod
    def calc_liquidation_isolated_price(cls, entry_price: float, leverage: float, maint_margin: float,
                                        taker_fee: float, funding_rate: float, position: str = 'short'):
        p = 1 if position == 'short' else -1
        result = round(
            entry_price / (
                    1 +
                    (-p * ((100 / leverage / 100) + 2 * taker_fee / 100)) +
                    (p * (maint_margin + taker_fee + funding_rate) / 100)
            ), 8)
        return result

    @classmethod
    def calc_liquidation_cross_price(cls, quantity: Union[int, float], entry_price: float, margin_balance: float,
                                     maint_margin: float, taker_fee: float, funding_rate: float,
                                     position: str = 'short'):
        p = 1 if position == 'short' else -1
        result = round(
            (p * quantity * entry_price) / (
                (-margin_balance * entry_price) +
                ((maint_margin + taker_fee + funding_rate) / 100 * quantity) +
                (p * quantity)
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
            if _symbol == "xbtusd":
                result = (1 / price, True)
            elif re.match(r'xbt[fghjkmnquvxz]\d{2}$', _symbol):
                result = (1 / price, True)
            elif _symbol == "xbtjpy":
                result = (100 / price, True)
            elif _symbol == "xbtkrw":
                result = (1000 / price, True)
            elif _symbol in ('xbt7d_u105', 'xbt7d_d95'):
                result = (0.1 * price, False)
            elif re.match(r'adausdt[fghjkmnquvxz]\d{2}', _symbol):
                result = (0.01 * price, False)
            elif _symbol in ('ethusd', 'bchusd'):
                result = (1e-6 * price, False)
            elif re.match(r'ethusd[fghjkmnquvxz]\d{2}', _symbol):
                result = (1e-6 * price, False)
            elif re.match(r'yfiusdt[fghjkmnquvxz]\d{2}', _symbol):
                result = (1e-7 * price, False)
            elif _symbol == 'ltcusd':
                result = (2e-6 * price, False)
            elif _symbol == 'linkusdt':
                result = (0.0001 * price, False)
            elif re.match(r'(bnb|dot|eos|link|xtz)usdt[fghjkmnquvxz]\d{2}', _symbol):
                result = (0.0001 * price, False)
            elif _symbol == 'xrpusd':
                result = (0.0002 * price, False)
            elif re.match(r'(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}', _symbol):
                result = (price, False)
            elif _symbol == 'ethxbt':
                result = (price, False)
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return result

    @classmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        _symbol = symbol.lower()
        result = None
        try:
            if _symbol == "xbtusd":
                result = 1 / face_price
            elif re.match(r'xbt[fghjkmnquvxz]\d{2}$', _symbol):
                result = 1 / face_price
            elif _symbol == "xbtjpy":
                result = 100 / face_price
            elif _symbol == "xbtkrw":
                result = 1000 / face_price
            elif _symbol in ('xbt7d_u105', 'xbt7d_d95'):
                result = 10 * face_price
            elif re.match(r'adausdt[fghjkmnquvxz]\d{2}', _symbol):
                result = 100 * face_price
            elif _symbol in ('ethusd', 'bchusd'):
                result = 1e+6 * face_price
            elif re.match(r'ethusd[fghjkmnquvxz]\d{2}', _symbol):
                result = 1e+6 * face_price
            elif re.match(r'yfiusdt[fghjkmnquvxz]\d{2}', _symbol):
                result = 1e+7 * face_price
            elif _symbol == 'ltcusd':
                result = 2e+6 * face_price
            elif _symbol == 'linkusdt':
                result = face_price / 0.0001
            elif re.match(r'(bnb|dot|eos|link|xtz)usdt[fghjkmnquvxz]\d{2}', _symbol):
                result = face_price / 0.0001
            elif _symbol == 'xrpusd':
                result = face_price / 0.0002
            elif re.match(r'(ada|bch|eos|eth|ltc|trx|xrp)[fghjkmnquvxz]\d{2}$', _symbol):
                result = face_price
            elif _symbol == 'ethxbt':
                result = face_price
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        return result
