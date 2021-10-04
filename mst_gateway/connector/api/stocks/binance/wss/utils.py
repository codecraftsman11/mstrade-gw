import json
from mst_gateway.connector.api.stocks.binance.utils import stock2symbol


def make_cmd(cmd, args, symbol=None):
    if isinstance(symbol, list) and symbol not in ('*', None):
        params = [f'{stock2symbol(s)}@{convert_args(args)}' for s in symbol]
    elif symbol not in ('*', None):
        params = [f'{stock2symbol(symbol)}@{convert_args(args)}']
    else:
        params = [args]
    return json.dumps({
        'method': cmd,
        'params': params,
        'id': 1
    })


def convert_args(args):
    if args == '!ticker@arr':
        args = 'ticker'
    elif args == '!bookTicker':
        args = 'bookTicker'
    elif args == '!markPrice@arr':
        args = 'markPrice'
    return args


def cmd_subscribe(subscr_name, symbol=None):
    return make_cmd("SUBSCRIBE", subscr_name, symbol)


def cmd_unsubscribe(subscr_name, symbol=None):
    return make_cmd("UNSUBSCRIBE", subscr_name, symbol)


def cmd_request(listen_key, channel_name):
    return make_cmd("REQUEST",  f'{listen_key}@{channel_name}')


def is_ok(response: str) -> bool:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return False
    return data.get('result', True) is None


def is_auth_ok(response: str) -> bool:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return False
    return not bool(data.get('error'))
