import time
from typing import Union, Optional
from websockets import client
from mst_gateway.connector.api.stocks.bitmex.lib.async_client import AsyncBitmexApiClient
from . import subscribers as subscr_class
from .router import BitmexWssRouter
from .utils import is_auth_ok, make_cmd
from .. import var
from ....wss import StockWssApi, ThrottleWss
from ....types import ExchangeDrivers


BITMEX_WSS_DEFAULT_TIMEOUT = 5


class BitmexWssApi(StockWssApi):
    driver = ExchangeDrivers.bitmex
    BASE_URL = "wss://ws.bitmex.com/realtime"
    TEST_URL = "wss://ws.testnet.bitmex.com/realtime"
    name = "bitmex"
    subscribers = {
        'symbol': subscr_class.BitmexSymbolSubscriber(),
        'quote_bin': subscr_class.BitmexQuoteBinSubscriber(),
        'order_book': subscr_class.BitmexOrderBookSubscriber(),
        'trade': subscr_class.BitmexTradeSubscriber()
    }

    auth_subscribers = {
        'order': subscr_class.BitmexOrderSubscriber(),
        'position': subscr_class.BitmexPositionSubscriber(),
        'wallet': subscr_class.BitmexWalletSubscriber()
    }

    router_class = BitmexWssRouter
    throttle = ThrottleWss(ws_limit=var.BITMEX_THROTTLE_LIMITS.get('ws'))

    async def _connect(self, **kwargs):
        kwargs['ws_options'] = {
            'max_size': 2 ** 24,
            'max_queue': 2 ** 13,
            'read_limit': 2 ** 18,
            'write_limit': 2 ** 18,
        }
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        res = await _ws.recv()
        self._logger.info(res)
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        if auth is None:
            auth = self._auth
        wss = self.handler
        expires = int(time.time()) + self._options.get('timeout', BITMEX_WSS_DEFAULT_TIMEOUT)
        signature = AsyncBitmexApiClient.generate_signature(auth.get('api_secret', ""), "GET", "/realtime", expires)
        await wss.send(make_cmd('authKeyExpires', [auth.get('api_key', ""), expires, signature]))
        self.auth_connect = is_auth_ok(await wss.recv())
        return self.auth_connect

    def _lookup_table(self, message: Union[dict, list]) -> Optional[dict]:
        if 'table' in message and isinstance(message, dict) and message.get('data'):
            return message
        return None

    def __split_message_map(self, key: str) -> Optional[callable]:
        _map = {
            'execution': self.split_order,
            'trade': self.split_trade,
        }
        return _map.get(key)

    def _split_message(self, message):
        method = self.__split_message_map(message['table'])
        if not method:
            return super()._split_message(message)
        return super()._split_message(method(message=message))

    def split_order(self, message: dict) -> list:
        _messages = list()
        _orders = message.pop('data', [])
        message.pop('action', None)
        for order in _orders:
            action = self.define_action_by_order_status(order.get('ordStatus'))
            _messages.append(dict(**message, action=action, data=[order]))
        return _messages

    def split_trade(self, message: dict) -> list:
        return [dict(**message, data=[trade]) for trade in message.pop('data', [])]

    def define_action_by_order_status(self, order_status: str) -> str:
        if order_status == var.BITMEX_ORDER_STATUS_NEW:
            return 'insert'
        elif order_status in var.BITMEX_ORDER_DELETE_ACTION_STATUSES:
            return 'delete'
        return 'update'
