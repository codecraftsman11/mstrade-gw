import time
from websockets import client
from . import subscribers as subscr
from .router import BitmexWssRouter
from .utils import is_auth_ok, make_cmd, parse_message
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
        'execution': subscr.BitmexExecutionSubscriber(),
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
