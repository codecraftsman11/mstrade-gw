import time
from logging import Logger
from websockets import client
from ....wss import StockWssApi
from ....wss.throttle import ThrottleWss
from ....wss.subscriber import Subscriber
from . import subscribers as subscr
from .utils import is_auth_ok, make_cmd
# from ..utils import bitmex_signature
from .router import BinanceWssRouter
bitmex_signature = 1

BITMEX_WSS_DEFAULT_TIMEOUT = 5


class BinanceWssApi(StockWssApi):
    BASE_URL = "wss://stream.binance.com:9443/ws"
    name = "binance"
    subscribers = {
        'order_book': subscr.BinanceOrderBookSubscriber(),
        'trade': subscr.BinanceTradeSubscriber(),
        'quote_bin': subscr.BinanceQuoteBinSubscriber(),
        'symbol': subscr.BinanceSymbolSubscriber()
    }

    auth_subscribers = {
        # 'order': subscr.BinanceOrderSubscriber(),
        # 'position': subscr.BinancePositionSubscriber(),
        # 'execution': subscr.BinanceExecutionSubscriber()
    }

    router_class = BinanceWssRouter

    def __init__(self,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 name: str = None,
                 throttle_rate: int = 30,
                 throttle_storage=None):
        super().__init__(url, auth, logger, options, name, throttle_rate)
        if throttle_storage:
            self.throttle = ThrottleWss(throttle_storage)

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        # res = await _ws.recv()
        self._logger.info('connected')
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
    #     if auth is None:
    #         auth = self._auth
    #     wss = self.handler
    #     expires = int(time.time()) + self._options.get('timeout', BITMEX_WSS_DEFAULT_TIMEOUT)
    #     signature = bitmex_signature(auth.get('api_secret', ""), "GET", "/realtime", expires)
    #     await wss.send(make_cmd('authKeyExpires', [auth.get('api_key', ""), expires,
    #                                                signature]))
    #     return is_auth_ok(await wss.recv())
        return True

    # def _get_subscriber(self, subscr_name: str) -> Subscriber:
    #     if subscr_name.lower() == "trade":
    #         return super()._get_subscriber("quote_bin")
    #     return super()._get_subscriber(subscr_name)

    def __setstate__(self, state):
        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        return state
