from typing import Union, Optional
from datetime import datetime


def load_symbol_data(raw_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = _date(raw_data.get('closeTime'))
    mark_price = _float(raw_data.get('lastPrice'))
    # face_price, _reversed = _face_price(symbol, mark_price)
    face_price, _reversed = None, None
    return {
        'time': symbol_time,
        'timestamp': raw_data.get('closeTime'),
        'symbol': symbol,
        'price': _float(raw_data.get('lastPrice')),
        'price24': _float(raw_data.get('weightedAvgPrice')),
        # 'pair': _get_symbol_pair(raw_data.get('symbol'),
        #                          raw_data.get('rootSymbol')),
        'pair': None,
        # 'tick': _float(raw_data.get('tickSize')),
        'tick': None,
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': _float(raw_data.get('bidPrice')),
        'ask_price': _float(raw_data.get('askPrice')),
        'reversed': _reversed
    }


def load_quote_data(raw_data: dict, symbol: str = None) -> dict:
    """
        {'id': 170622457,
        'isBestMatch': True,
        'isBuyerMaker': True,
        'price': '0.02107500',
        'qty': '17.75100000',
        'quoteQty': '0.37410232',
        'time': 1585491048725}
    """
    return {
        'time': _date(raw_data.get('time')),
        'timestamp': raw_data.get('time'),
        'symbol': symbol,
        'price': _float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        # 'side': load_order_side(raw_data.get('side'))
        'side': None
    }


def load_quote_bin_data(raw_data: list, symbol: str = None) -> dict:
    return {
        'time': _date(raw_data[0]),
        'timestamp': raw_data[0],
        'symbol': symbol,
        'open': _float(raw_data[1]),
        'close': _float(raw_data[4]),
        'high': _float(raw_data[2]),
        'low': _float(raw_data[3]),
        'volume': raw_data[5],
    }


def _date(token: Union[datetime, int]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.fromtimestamp(token/1000)
    except ValueError:
        return None


def _float(token: Union[int, float, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None
