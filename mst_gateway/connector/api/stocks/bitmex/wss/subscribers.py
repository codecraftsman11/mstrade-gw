from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from asyncio import CancelledError
from websockets.exceptions import ConnectionClosedError
from .utils import cmd_subscribe, cmd_unsubscribe
from ....wss.subscriber import Subscriber
from ......storage.var import StateStorageKey

if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexSubscriber(Subscriber):
    subscriptions = ()

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        for subscription in self.subscriptions:
            if not api.handler or api.handler.closed:
                return False
            try:
                await api.handler.send(cmd_subscribe(subscription, symbol))
            except (CancelledError, ConnectionClosedError) as e:
                api.logger.warning(f"{self.__class__.__name__} - {e}")
                return False
        return True

    async def _unsubscribe(self, api: BitmexWssApi, symbol=None):
        for subscription in self.subscriptions:
            if not api.handler or api.handler.closed:
                return True
            try:
                await api.handler.send(cmd_unsubscribe(subscription, symbol))
            except (CancelledError, ConnectionClosedError) as e:
                api.logger.warning(f"{self.__class__.__name__} - {e}")
        return True


class BitmexSymbolSubscriber(BitmexSubscriber):
    subscription = "symbol"
    subscriptions = ("instrument",)
    is_close_connection = False


class BitmexQuoteBinSubscriber(BitmexSubscriber):
    subscription = "quote_bin"
    subscriptions = ("tradeBin1m", "trade")
    is_close_connection = False


class BitmexOrderBookSubscriber(BitmexSubscriber):
    subscription = "order_book"
    subscriptions = ("orderBookL2_25",)
    is_close_connection = False


class BitmexTradeSubscriber(BitmexSubscriber):
    subscription = "trade"
    subscriptions = ("trade",)
    is_close_connection = False


class BitmexWalletSubscriber(BitmexSubscriber):
    subscription = "wallet"
    subscriptions = ("margin",)

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        if 'wallet' in api.subscriptions:
            return True
        return await super()._subscribe(api)

    async def subscribe_exchange_rates(self, api: BitmexWssApi):
        redis = await api.storage.get_client()
        state_channel = (await redis.subscribe(f"{StateStorageKey.exchange_rates}.{api.name}.{api.schema}"))[0]
        while await state_channel.wait_message():
            state_data = await state_channel.get_json()
            exchange_rates = state_data.get(api.name.lower(), {}).get(api.schema, {})
            api.partial_state_data[self.subscription].update({'exchange_rates': exchange_rates})

    async def init_partial_state(self, api: BitmexWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.subscribe_exchange_rates(api)))
        exchange_rates = await api.storage.get(f"{StateStorageKey.exchange_rates}.{api.name}.{api.schema}")
        return {'exchange_rates': exchange_rates}


class BitmexOrderSubscriber(BitmexSubscriber):
    subscription = "order"
    subscriptions = ("execution",)


class BitmexPositionSubscriber(BitmexWalletSubscriber):
    subscription = "position"
    subscriptions = ("position",)
