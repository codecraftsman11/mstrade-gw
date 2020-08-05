import datetime
import json
import random
import sys
import inspect


def j_dumps(struct) -> str:
    return json.dumps(struct, default=_convert)


def j_q(src: str) -> dict:
    return json.loads(src)


def fetch_data(data, path=None, default=None):
    if not isinstance(data, dict):
        raise TypeError("Data to fetch value from is not a dict")
    if path is None:
        return data
    if not isinstance(path, str):
        raise TypeError("Path of value fetched from dict is not a sting")
    if path[0] != '.':
        return data.get(path, default)
    return None


def generate_order_id():
    random.seed()  # nosec
    return "test.{}".format(random.randint(0, sys.maxsize))  # nosec


def _convert(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    return None


class ClassWithAttributes:
    @classmethod
    def _attributes(cls):
        attributes = inspect.getmembers(
            cls,
            lambda a: not (inspect.isroutine(a) or inspect.isdatadescriptor(a)))
        return [i for i in attributes if not i[0].startswith('__')]

    @classmethod
    def is_valid(cls, value) -> bool:
        for attr in cls._attributes():
            if value == attr[1]:
                return True
        return False

    @classmethod
    def keys(cls) -> tuple:
        return tuple(i[0] for i in cls._attributes())

    @classmethod
    def values(cls) -> tuple:
        return tuple(i[1] for i in cls._attributes())

    @classmethod
    def items(cls) -> dict:
        return {i[0]: i[1] for i in cls._attributes()}
