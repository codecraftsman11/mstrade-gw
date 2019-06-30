import time
from logging import Logger
from websockets import client
from ....wss import StockWssApi
from . import subscribers as subscr
from .utils import is_auth_ok
from .utils import make_cmd
from ..utils import bitmex_signature
from .router import BitmexWssRouter


BITMEX_WSS_DEFAULT_TIMEOUT = 5


class BitmexWssApi(StockWssApi):
    BASE_URL = "wss://www.bitmex.com/realtime"
    TEST_URL = "wss://testnet.bitmex.com/realtime"
    name = "Bitmex"
    subscribers = {
        'symbol': subscr.BitmexSymbolSubscriber(),
        'quote_bin': subscr.BitmexQuoteBinSubscriber(),
    }

    auth_subscribers = {
        'order': subscr.BitmexOrderSubscriber()
    }

    router = BitmexWssRouter()

    def __init__(self,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None,
                 timeout: int = None):
        self._timeout = timeout or BITMEX_WSS_DEFAULT_TIMEOUT
        super().__init__(url, auth, logger)

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        res = await _ws.recv()
        self._logger.info(res)
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        if auth is None:
            auth = self._auth
        wss = self.handler
        expires = int(time.time()) + self._timeout
        signature = bitmex_signature(auth.get('api_secret', ""), "GET", "/realtime", expires)
        await wss.send(make_cmd('authKeyExpires', [auth.get('api_key', ""), expires,
                                                   signature]))
        return is_auth_ok(await wss.recv())
