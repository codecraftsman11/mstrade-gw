from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio
from websockets import client
from websockets.exceptions import ConnectionClosedError
from .utils import cmd_subscribe, cmd_unsubscribe
from ....wss.subscriber import Subscriber

if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexSubscriber(Subscriber):
    subscriptions = ()

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.subscriptions:
            try:
                await wss.send(cmd_subscribe(subscription, symbol))
            except (asyncio.exceptions.CancelledError, ConnectionClosedError) as e:
                api.logger.warning(e)
                return False
        return True

    async def _unsubscribe(self, api: BitmexWssApi, symbol=None):
        wss: client = api.handler
        for subscription in self.subscriptions:
            await wss.send(cmd_unsubscribe(subscription, symbol))
        return True


class BitmexSymbolSubscriber(BitmexSubscriber):
    subscriptions = ("instrument", "quote")


class BitmexQuoteBinSubscriber(BitmexSubscriber):
    subscriptions = ("trade", "tradeBin1m")


class BitmexOrderSubscriber(BitmexSubscriber):
    subscriptions = ("execution",)


class BitmexPositionSubscriber(BitmexSubscriber):
    subscriptions = ("position",)


class BitmexOrderBookSubscriber(BitmexSubscriber):
    subscriptions = ("orderBookL2_25",)


class BitmexTradeSubscriber(BitmexSubscriber):
    subscriptions = ("trade",)


class BitmexWalletSubscriber(BitmexSubscriber):
    subscriptions = ("margin",)

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        if 'wallet' in api.subscriptions:
            return True
        return await super()._subscribe(api)
