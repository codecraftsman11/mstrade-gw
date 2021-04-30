from __future__ import annotations
import asyncio
from asyncio import CancelledError
from typing import TYPE_CHECKING, Optional
from websockets.exceptions import ConnectionClosedError

from mst_gateway.exceptions import QueryError
from .. import utils
from ..lib import AsyncClient
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
        redis = await api.storage.get_client()
        symbol_channel = (await redis.subscribe('symbol'))[0]
        while api.handler and not api.handler.closed:
            while await symbol_channel.wait_message():
                if symbols := await symbol_channel.get_json():
                    new_registered_symbols = set(symbols.get(api.name, {}).get(api.schema, {}))
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
    subscription = "order_book"
    subscriptions = ("depth",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceTradeSubscriber(BinanceSubscriber):
    subscription = "trade"
    subscriptions = ("trade",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceQuoteBinSubscriber(BinanceSubscriber):
    subscription = "quote_bin"
    subscriptions = ("kline_1m",)
    general_subscribe_available = False
    is_close_connection = False


class BinanceSymbolSubscriber(BinanceSubscriber):
    subscription = "symbol"
    subscriptions = ("!ticker@arr",)
    is_close_connection = False


class BinanceFuturesSymbolSubscriber(BinanceSubscriber):
    subscription = "symbol"
    subscriptions = ("!ticker@arr", "!bookTicker")
    is_close_connection = False


class BinanceWalletSubscriber(BinanceSubscriber):
    subscription = "wallet"
    subscriptions = ()


class BinanceOrderSubscriber(BinanceSubscriber):
    subscription = "order"
    subscriptions = ()


class BinanceFuturesPositionSubscriber(BinanceSubscriber):
    subscription = "position"
    subscriptions = ("!markPrice@arr",)
    detail_subscribe_available = False

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        async with AsyncClient(
                api_key=api.auth['api_key'], api_secret=api.auth['api_secret'], test=api.test
        ) as client:
            try:
                position_state = await client.futures_account_v2()
                leverage_brackets = await client.futures_leverage_bracket()
                return {
                    'position_state': utils.load_positions_state(position_state),
                    'leverage_brackets': utils.load_futures_leverage_brackets_as_dict(leverage_brackets)
                }
            except Exception as e:
                raise QueryError(f"Init partial state error: {e}")
