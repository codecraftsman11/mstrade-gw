import json
from mst_gateway.connector.api.stocks.binance.utils import stock2symbol


def make_cmd(cmd, args, symbol=None):
    if symbol is not None:
        symbol = stock2symbol(symbol)
        if args == '!ticker@arr':
            args = 'ticker'
        args = f'{symbol}@{args}'
    return json.dumps({
        'method': cmd,
        'params': [args],
        'id': 1
    })


def cmd_subscribe(subscr_name, symbol=None):
    return make_cmd("SUBSCRIBE", subscr_name, symbol)


def cmd_unsubscribe(subscr_name, symbol=None):
    return make_cmd("UNSUBSCRIBE", subscr_name, symbol)


def is_ok(response: str) -> bool:
    data = json.loads(response)
    return bool(data.get('success'))


def is_auth_ok(response: str) -> bool:
    data = json.loads(response)
    return not bool(data.get('error'))


def parse_message(message: str) -> dict:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {'raw': message}
