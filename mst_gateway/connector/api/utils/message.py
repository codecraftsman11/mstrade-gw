import json
from typing import Union


def parse_message(message) -> Union[dict, list, None]:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {'raw': message}
    except Exception:
        return None


def dump_message(data) -> Union[str, list, None]:
    try:
        return json.dumps(data)
    except TypeError:
        return str(data)
    except Exception:
        return None
