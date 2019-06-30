from __future__ import annotations
from typing import TYPE_CHECKING
from websockets import client
from ....wss.subscriber import Subscriber
from .utils import cmd_subscribe
from .utils import cmd_unsubscribe

if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexSubscriber(Subscriber):
    subscriptions = ()

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.__class__.subscriptions:
            await wss.send(cmd_subscribe(subscription, symbol))
        return True

    async def _unsubscribe(self, api: BitmexWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.__class__.subscriptions:
            await wss.send(cmd_unsubscribe(subscription, symbol))
        return True


class BitmexSymbolSubscriber(BitmexSubscriber):
    subscriptions = ("instrument",)


class BitmexQuoteBinSubscriber(BitmexSubscriber):
    subscriptions = ("trade", "tradeBin1m")


class BitmexOrderSubscriber(BitmexSubscriber):
    subscriptions = ("order",)
