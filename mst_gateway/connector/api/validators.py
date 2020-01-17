from datetime import datetime
from .. import api


def side_valid(value):
    try:
        return isinstance(value, int) and value in [api.SELL, api.BUY]
    except Exception:
        return False


def order_id_valid(value):
    try:
        return isinstance(value, str) and value
    except Exception:
        return False


def type_valid(value):
    try:
        return isinstance(value, int) and value in (api.MARKET, api.LIMIT, api.STOP,
                                                    api.STOPLIMIT, api.TP, api.TPLIMIT)
    except Exception:
        return False


def datetime_valid(value):
    if isinstance(value, datetime):
        return True
    try:
        datetime.strptime(value, api.DATETIME_FORMAT)
    except ValueError:
        return False
    return True


def pair_valid(value: list) -> bool:
    if not isinstance(value, list):
        return False
    if len(value) != 2:
        return False
    if not isinstance(value[0], str):
        return False
    if not isinstance(value[1], str):
        return False
    return value[0] and value[1]