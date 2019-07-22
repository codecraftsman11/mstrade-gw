import json


def make_cmd(cmd, args, symbol=None):
    if symbol is not None:
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
    data = json.loads(response)
    return bool(data.get('success'))


def is_auth_ok(response: str) -> bool:
    data = json.loads(response)
    print(data)
    return not bool(data.get('error'))


def parse_message(message: str) -> dict:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {'raw': message}
