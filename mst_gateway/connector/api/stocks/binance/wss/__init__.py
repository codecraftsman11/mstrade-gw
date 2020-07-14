from websockets import client
from ....wss import StockWssApi
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

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        self._logger.info('Binance ws connected successful.')
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        return True
