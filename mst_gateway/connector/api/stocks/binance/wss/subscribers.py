from __future__ import annotations
from typing import TYPE_CHECKING
from websockets import client
from ....wss.subscriber import Subscriber
from .utils import cmd_subscribe
from .utils import cmd_unsubscribe

if TYPE_CHECKING:
    from . import BinanceWssApi


class BinanceSubscriber(Subscriber):
    subscriptions = ()

    async def _subscribe(self, api: BinanceWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.__class__.subscriptions:
            await wss.send(cmd_subscribe(subscription, symbol))
        return True

    async def _unsubscribe(self, api: BinanceWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.__class__.subscriptions:
            await wss.send(cmd_unsubscribe(subscription, symbol))
        return True


class BinanceOrderBookSubscriber(BinanceSubscriber):
    subscriptions = ("depth",)


class BinanceTradeSubscriber(BinanceSubscriber):
    subscriptions = ("trade",)


class BinanceQuoteBinSubscriber(BinanceSubscriber):
    subscriptions = ("kline_1m",)


class BinanceSymbolSubscriber(BinanceSubscriber):
    subscriptions = ("!ticker@arr",)


class BinanceFuturesSymbolSubscriber(BinanceSymbolSubscriber):
    subscriptions = ("!ticker@arr", "!bookTicker")
