from __future__ import annotations
import asyncio
from asyncio import CancelledError
from typing import TYPE_CHECKING
from websockets.exceptions import ConnectionClosedError
from ....wss.subscriber import Subscriber
from .utils import cmd_subscribe, cmd_unsubscribe


if TYPE_CHECKING:
    from . import BinanceWssApi


class BinanceSubscriber(Subscriber):

    async def _subscribe(self, api: BinanceWssApi, symbol=None):
        if not api.handler or api.handler.closed:
            return False
        for subscription in self.subscriptions:
            if symbol in ('*', None) and not self.general_subscribe_available:
                asyncio.create_task(self.send_command(cmd_subscribe, api, subscription))
            else:
                await asyncio.sleep(1)
                try:
                    await api.handler.send(cmd_subscribe(subscription, symbol))
                except (CancelledError, ConnectionClosedError) as e:
                    api.logger.warning(f"{self.__class__.__name__} - {e}")
                    return False
        return True

    async def _unsubscribe(self, api: BinanceWssApi, symbol=None):
        if not api.handler or api.handler.closed:
            return True
        for subscription in self.subscriptions:
            if symbol in ('*', None) and not self.general_subscribe_available:
                asyncio.create_task(self.send_command(cmd_unsubscribe, api, subscription))
            else:
                await asyncio.sleep(1)
                try:
                    await api.handler.send(cmd_unsubscribe(subscription, symbol))
                except (CancelledError, ConnectionClosedError) as e:
                    api.logger.warning(f"{self.__class__.__name__} - {e}")
        return True

    async def send_command(self, command: callable, api: BinanceWssApi, subscription: str):
        symbols = [s for s in api.storage.get('symbol', api.name, api.schema)]
        symbols_count = len(symbols)
        try:
            for i in range(0, symbols_count, 400):
                await asyncio.sleep(1)
                await api.handler.send(command(subscription, symbols[i:i+400]))
        except (CancelledError, ConnectionClosedError) as e:
            api.logger.warning(f"{self.__class__.__name__} - {e}")


class BinanceOrderBookSubscriber(BinanceSubscriber):
    subscriptions = ("depth",)
    general_subscribe_available = False


class BinanceTradeSubscriber(BinanceSubscriber):
    subscriptions = ("trade",)
    general_subscribe_available = False


class BinanceQuoteBinSubscriber(BinanceSubscriber):
    subscriptions = ("kline_1m",)
    general_subscribe_available = False


class BinanceSymbolSubscriber(BinanceSubscriber):
    subscriptions = ("!ticker@arr",)


class BinanceFuturesSymbolSubscriber(BinanceSubscriber):
    subscriptions = ("!ticker@arr", "!bookTicker")


class BinanceWalletSubscriber(BinanceSubscriber):
    subscriptions = ()


class BinanceOrderSubscriber(BinanceSubscriber):
    subscriptions = ()
