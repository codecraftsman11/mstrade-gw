import json
from ..utils import symbol2stock


def make_cmd(cmd, args, symbol=None):
    if symbol not in ('*', None):
        symbol = symbol2stock(symbol)
        args = f"{args}:{symbol}"
    return json.dumps({
        'op': cmd,
        'args': args
    })


def cmd_subscribe(subscr_name, symbol=None):
    return make_cmd("subscribe", subscr_name, symbol)


def cmd_unsubscribe(subscr_name, symbol=None):
    return make_cmd("unsubscribe", subscr_name, symbol)


def is_ok(response: str) -> bool:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return False
    return bool(data.get('success'))


def is_auth_ok(response: str) -> bool:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return False
    return not bool(data.get('error'))
