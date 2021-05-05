from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from asyncio import CancelledError
from websockets.exceptions import ConnectionClosedError
from .utils import cmd_subscribe, cmd_unsubscribe
from ....wss.subscriber import Subscriber

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


class BitmexOrderSubscriber(BitmexSubscriber):
    subscription = "order"
    subscriptions = ("execution",)


class BitmexPositionSubscriber(BitmexSubscriber):
    subscription = "position"
    subscriptions = ("position",)


class BitmexWalletSubscriber(BitmexSubscriber):
    subscription = "wallet"
    subscriptions = ("margin",)

    async def _subscribe(self, api: BitmexWssApi, symbol=None):
        if 'wallet' in api.subscriptions:
            return True
        return await super()._subscribe(api)

    async def subscribe_currency_state(self, api: BitmexWssApi):
        redis = await api.storage.get_client()
        state_channel = (await redis.subscribe('currency'))[0]
        while await state_channel.wait_message():
            if state_data := await state_channel.get_json():
                currency_state = state_data.get(api.name.lower(), {}).get(api.schema, {})
                api.partial_state_data[self.subscription].setdefault('currency_state', {})
                api.partial_state_data[self.subscription]['currency_state'] = currency_state
                if wallet_serializer := api.router.serializers.get(self.subscription):
                    wallet_serializer.currency_state = currency_state

    async def init_partial_state(self, api: BitmexWssApi) -> dict:
        asyncio.create_task(self.subscribe_currency_state(api))
        currency_state = await api.storage.get('currency', exchange=api.name, schema=api.schema)
        return {'currency_state': currency_state}
