import time
from websockets import client
from . import subscribers as subscr
from .router import BitmexWssRouter
from .utils import is_auth_ok, make_cmd, parse_message
from .. import var
from ..lib import bitmex_signature
from ...binance.wss import dump_message
from ....wss import StockWssApi
from ....wss.subscriber import Subscriber

BITMEX_WSS_DEFAULT_TIMEOUT = 5


class BitmexWssApi(StockWssApi):
    BASE_URL = "wss://www.bitmex.com/realtime"
    TEST_URL = "wss://testnet.bitmex.com/realtime"
    name = "bitmex"
    subscribers = {
        'symbol': subscr.BitmexSymbolSubscriber(),
        'quote_bin': subscr.BitmexQuoteBinSubscriber(),
        'order_book': subscr.BitmexOrderBookSubscriber(),
        # 'trade': subscr.BitmexTradeSubscriber()
    }

    auth_subscribers = {
        'order': subscr.BitmexOrderSubscriber(),
        'position': subscr.BitmexPositionSubscriber(),
        'wallet': subscr.BitmexWalletSubscriber()
    }

    router_class = BitmexWssRouter

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        res = await _ws.recv()
        self._logger.info(res)
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        if auth is None:
            auth = self._auth
        wss = self.handler
        expires = int(time.time()) + self._options.get('timeout', BITMEX_WSS_DEFAULT_TIMEOUT)
        signature = bitmex_signature(auth.get('api_secret', ""), "GET", "/realtime", expires)
        await wss.send(make_cmd('authKeyExpires', [auth.get('api_key', ""), expires,
                                                   signature]))
        self.auth_connect = is_auth_ok(await wss.recv())
        return self.auth_connect

    def _get_subscriber(self, subscr_name: str) -> Subscriber:
        if subscr_name.lower() == "trade":
            return super()._get_subscriber("quote_bin")
        return super()._get_subscriber(subscr_name)

    def _split_message(self, message):
        data = parse_message(message)
        for method in (
            self.split_order,
        ):
            _tmp = method(data=data)
            if _tmp:
                return _tmp
        return message

    def split_order(self, data, **kwargs):
        if isinstance(data, dict) and data.get('table') == 'execution':
            _data = list()
            for order_data in data.get('data', []):
                action = self.define_action_by_order_status(order_data.get('ordStatus'))
                _data.append(dump_message(dict(table='execution', action=action,  data=[order_data])))
            return _data

    def define_action_by_order_status(self, order_status: str) -> str:
        if order_status == var.BITMEX_ORDER_STATUS_NEW:
            return 'insert'
        elif order_status in var.BITMEX_ORDER_DELETE_ACTION_STATUSES:
            return 'delete'
        return 'update'
