import time
from typing import Union, Optional
from websockets import client
from . import subscribers as subscr
from .router import BitmexWssRouter
from .utils import is_auth_ok, make_cmd
from .. import var
from ..lib import bitmex_signature
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

    def _lookup_table(self, message: Union[dict, list]) -> Optional[dict]:
        if 'table' in message and isinstance(message, dict) and message.get('data'):
            return message
        return None

    def __split_message_map(self, key: str) -> Optional[callable]:
        _map = {
            'execution': self.split_order,
        }
        return _map.get(key)

    def _split_message(self, message):
        method = self.__split_message_map(message['table'])
        if not method:
            return super()._split_message(message)
        return super()._split_message(method(message=message))

    def split_order(self, message):
        _messages = list()
        _orders = message.pop('data', [])
        message.pop('action', None)
        for order in _orders:
            action = self.define_action_by_order_status(order.get('ordStatus'))
            _messages.append(dict(**message, action=action, data=[order]))
        return _messages

    def define_action_by_order_status(self, order_status: str) -> str:
        if order_status == var.BITMEX_ORDER_STATUS_NEW:
            return 'insert'
        elif order_status in var.BITMEX_ORDER_DELETE_ACTION_STATUSES:
            return 'delete'
        return 'update'
