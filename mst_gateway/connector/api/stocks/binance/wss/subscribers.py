from __future__ import annotations
import asyncio
from asyncio import CancelledError
from typing import TYPE_CHECKING, Optional
from websockets.exceptions import ConnectionClosedError
from ....wss.subscriber import Subscriber
from .utils import cmd_subscribe, cmd_unsubscribe


if TYPE_CHECKING:
    from . import BinanceWssApi


class BinanceSubscriber(Subscriber):

    def __init__(self):
        super().__init__()
        self._task_watcher: Optional[asyncio.Task] = None
        self._subscribed_symbols = set()

    async def _subscribe(self, api: BinanceWssApi, symbol=None):
        for subscription in self.subscriptions:
            if symbol in ('*', None) and not self.general_subscribe_available:
                symbols = api.state_symbol_list
                # run task watcher for new symbols
                self._subscribed_symbols = set(symbols)
                self._task_watcher = asyncio.create_task(self.subscribe_watcher(api))
                asyncio.create_task(
                    self.send_command(cmd_subscribe, api, subscription, symbols)
                )
            elif symbol not in ('*', None) and not self.detail_subscribe_available:
                try:
                    await api.handler.send(cmd_subscribe(subscription))
                except (CancelledError, ConnectionClosedError) as e:
                    api.logger.warning(f"{self.__class__.__name__} - {e}")
                    return False
            else:
                if not api.handler or api.handler.closed:
                    return False
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
                # stop task watcher for new symbols
                if self._task_watcher is not None:
                    self._task_watcher.cancel()
                asyncio.create_task(
                    self.send_command(cmd_unsubscribe, api, subscription, list(self._subscribed_symbols))
                )
            elif symbol not in ('*', None) and not self.detail_subscribe_available:
                if not api.handler or api.handler.closed:
                    return True
                try:
                    await api.handler.send(cmd_unsubscribe(subscription))
                except (CancelledError, ConnectionClosedError) as e:
                    api.logger.warning(f"{self.__class__.__name__} - {e}")
            else:
                if not api.handler or api.handler.closed:
                    return True
                try:
                    await api.handler.send(cmd_unsubscribe(subscription, symbol))
                except (CancelledError, ConnectionClosedError) as e:
                    api.logger.warning(f"{self.__class__.__name__} - {e}")
        return True

    async def send_command(self, command: callable, api: BinanceWssApi, subscription: str, symbols: list):
        symbols_count = len(symbols)
        try:
            for i in range(0, symbols_count, 400):
                await asyncio.sleep(1)
                if not api.handler or api.handler.closed:
                    return
                await api.handler.send(command(subscription, symbols[i:i+400]))
        except (CancelledError, ConnectionClosedError) as e:
            api.logger.warning(f"{self.__class__.__name__} - {e}")

    async def subscribe_watcher(self, api: BinanceWssApi):
        """
        watcher for new symbol when `general_subscribe_available` is False
        """
        while api.handler and not api.handler.closed:
            await asyncio.sleep(api.state_refresh_period)
            new_registered_symbols = set(api.state_symbol_list)
            unsubscribe_symbols = self._subscribed_symbols.difference(new_registered_symbols)
            subscribe_symbols = new_registered_symbols.difference(self._subscribed_symbols)
            for symbol in unsubscribe_symbols:
                await asyncio.sleep(1)
                await self._unsubscribe(api, symbol)
            for symbol in subscribe_symbols:
                await asyncio.sleep(1)
                await self._subscribe(api, symbol)
            self._subscribed_symbols = new_registered_symbols


class BinanceOrderBookSubscriber(BinanceSubscriber):
    subscriptions = ("depth",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceTradeSubscriber(BinanceSubscriber):
    subscriptions = ("trade",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceQuoteBinSubscriber(BinanceSubscriber):
    subscriptions = ("kline_1m",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceSymbolSubscriber(BinanceSubscriber):
    subscriptions = ("!ticker@arr",)
    is_close_connection = False


class BinanceFuturesSymbolSubscriber(BinanceSubscriber):
    subscriptions = ("!ticker@arr", "!bookTicker")
    is_close_connection = False


class BinanceWalletSubscriber(BinanceSubscriber):
    subscriptions = ()


class BinanceOrderSubscriber(BinanceSubscriber):
    subscriptions = ()


class BinanceFuturesPositionSubscriber(BinanceSubscriber):
    subscriptions = ("!markPrice@arr",)
    detail_subscribe_available = False
