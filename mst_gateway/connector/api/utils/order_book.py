from typing import Optional
from mst_gateway.connector.api import BUY, SELL


def pad_order_book(data: list, tick_size: float) -> list:
    mid = _ob_middle_index(data)
    if not mid:
        return data
    dim_s = data[0] - data[mid - 1]
    dim_b = data[mid] - data[-1]
    if dim_s > dim_b:
        return _pad_ob_side(data, tick_size, BUY)
    return _pad_ob_side(data, tick_size, SELL)


def _pad_ob_side(data, tick_size, side):
    # pylint: disable=unused-argument
    # TODO: fill the order book with gaps
    return data


def _ob_middle_index(data: list) -> Optional[int]:
    if not data:
        return None
    side = data[0]['side']
    for k, in enumerate(data):
        if data[k]['side'] != side:
            return k
    return None
