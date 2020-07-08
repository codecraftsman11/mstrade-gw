import time
from logging import Logger
from websockets import client
from ....wss import StockWssApi
from ....wss.throttle import ThrottleWss
from . import subscribers as subscr
from .utils import is_auth_ok, make_cmd
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
        self._logger.info('Binance ws connected successful.')
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        return True

    def __setstate__(self, state):
        self.__dict__ = state

    def __getstate__(self):
        state = self.__dict__.copy()
        return state
