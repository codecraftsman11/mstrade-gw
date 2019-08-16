import datetime
import json
import random
import sys


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
