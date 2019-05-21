import json


def _j(struct) -> str:
    return json.dumps(struct)


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
