from datetime import datetime
from schema import SchemaError
from mst_gateway.connector import api


def side_valid(value):
    if isinstance(value, int) and value in [api.SELL, api.BUY]:
        return value
    raise SchemaError('Invalid side')


def type_valid(value):
    if api.OrderType.is_valid(value):
        return value
    raise SchemaError('Invalid type')


def schema_valid(value):
    if api.OrderSchema.is_valid(value):
        return value
    raise SchemaError('Invalid schema field')


def datetime_valid(value):
    if isinstance(value, datetime):
        return value
    try:
        datetime.strptime(value, api.DATETIME_FORMAT)
    except ValueError:
        raise SchemaError('Invalid datetime field')
    return value


def iso_datetime_valid(value):
    if not isinstance(value, str):
        raise SchemaError('Invalid iso datetime field')
    try:
        datetime.strptime(value, api.DATETIME_FORMAT)
    except ValueError:
        raise SchemaError('Invalid iso datetime field')
    return value


def pair_valid(value: list):
    if not isinstance(value, list):
        raise SchemaError('Invalid pair field')
    if len(value) != 2:
        raise SchemaError('Invalid pair field')
    if not isinstance(value[0], str):
        raise SchemaError('Invalid pair field')
    if not isinstance(value[1], str):
        raise SchemaError('Invalid pair field')
    if value[0] and value[1]:
        return value
    raise SchemaError('Invalid pair field')


def leverage_type_valid(value):
    if api.LeverageType.is_valid(value):
        return value
    raise SchemaError('Invalid leverage_type')


def state_valid(value):
    if api.OrderState.is_valid(value):
        return value
    raise SchemaError('Invalid state')


def float_valid(value):
    if value is None or isinstance(value, (float, int)):
        return value
    raise SchemaError('Invalid float field')


def data_valid(data, rules):
    if not isinstance(data, dict):
        raise TypeError("Data is not dictionary")
    if not set(data.keys()) == set(rules.keys()):
        raise ValueError("Keys differ")
    for k in data:
        if not value_valid(data[k], rules[k]):
            raise ValueError("Invalid {}".format(k))
    return True


def data_update_valid(data, rules):
    if not isinstance(data, dict):
        raise TypeError("Data is not dictionary")
    if set(data.keys()) - set(rules.keys()):
        raise ValueError("In data present keys out of rule's range")
    for k in data:
        if not value_valid(data[k], rules[k]):
            raise ValueError("Invalid {}".format(k))
    return True


def value_valid(value, rule):
    if isinstance(rule, type):
        try:
            return value is None or isinstance(value, rule)
        except Exception:
            return False
    if callable(rule):
        return rule(value)
    return True


def position_mode_valid(value):
    if api.PositionMode.is_valid(value):
        return value
    raise SchemaError('Invalid position mode')


def position_side_valid(value):
    if api.PositionSide.is_valid(value):
        return value
    raise SchemaError('Invalid position side')
