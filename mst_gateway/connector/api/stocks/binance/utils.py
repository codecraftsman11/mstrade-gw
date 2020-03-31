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


def load_trade_data(raw_data: dict) -> dict:
    """{
        "id": 28457,
        "price": "4.00000100",
        "qty": "12.00000000",
        "commission": "10.10000000",
        "commissionAsset": "BNB",
        "time": 1499865549590,
        "isBuyer": true,
        "isMaker": false,
        "isBestMatch": true
    }"""
    return load_quote_data(raw_data)


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


def load_order_data(raw_data: dict, skip_undef=False) -> dict:
    data = {
        'order_id': raw_data.get('orderId') or raw_data.get('clientOrderId'),
        'symbol': raw_data.get('symbol'),
        'origQty': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPrice'),
        'type': raw_data.get('type'),
        'side': raw_data.get('side'),
        'price': _float(raw_data.get('price')),
        'created': _date(raw_data.get('time')),
        'active': raw_data.get('status') != "NEW",
        # 'schema': api.OrderSchema.margin1
    }
    return data


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
