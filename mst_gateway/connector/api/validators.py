from datetime import datetime
from .. import api


def side_valid(value):
    try:
        return isinstance(value, int) and value in [api.SELL, api.BUY]
    except Exception:
        return False


def exchange_order_id_valid(value):
    return value and isinstance(value, (int, str))


def type_valid(value):
    return api.OrderType.is_valid(value)


def schema_valid(value):
    return api.OrderSchema.is_valid(value)


def execution_valid(value):
    return api.OrderExec.is_valid(value)


def datetime_valid(value):
    if isinstance(value, datetime):
        return True
    try:
        datetime.strptime(value, api.DATETIME_FORMAT)
    except ValueError:
        return False
    return True


def iso_datetime_valid(value):
    if not isinstance(value, str):
        return False
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


def leverage_type_valid(value):
    return api.LeverageType.is_valid(value)
