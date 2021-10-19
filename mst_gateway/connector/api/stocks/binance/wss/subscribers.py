from __future__ import annotations
import asyncio
from asyncio import CancelledError
from typing import TYPE_CHECKING, Optional
from websockets.exceptions import ConnectionClosedError

from mst_gateway.exceptions import QueryError
from .. import utils
from ..lib import AsyncClient
from ....wss.subscriber import Subscriber
from ......storage.var import StateStorageKey
from .utils import cmd_subscribe, cmd_unsubscribe, cmd_request


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

    async def send_request(self, command: callable, api: BinanceWssApi, channel_name: str):
        try:
            if not api.handler or api.handler.closed:
                return
            await api.handler.send(command(api.listen_key, channel_name))
        except (CancelledError, ConnectionClosedError) as e:
            api.logger.warning(f"{self.__class__.__name__} - {e}")

    async def subscribe_watcher(self, api: BinanceWssApi):
        """
        watcher for new symbol when `general_subscribe_available` is False
        """
        redis = await api.storage.get_client()
        symbol_channel = (await redis.subscribe(StateStorageKey.symbol))[0]
        while api.handler and not api.handler.closed:
            while await symbol_channel.wait_message():
                symbols = await symbol_channel.get_json()
                new_registered_symbols = set(symbols.get(api.name.lower(), {}).get(api.schema, {}))
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


class BinanceFuturesSymbolSubscriber(BinanceSymbolSubscriber):
    subscriptions = ("!ticker@arr", "!bookTicker", "!markPrice@arr")


class BinanceWalletSubscriber(BinanceSubscriber):
    subscription = "wallet"
    subscriptions = ()

    async def subscribe_exchange_rates(self, api: BinanceWssApi):
        redis = await api.storage.get_client()
        state_channel = (await redis.subscribe(StateStorageKey.exchange_rates))[0]
        while await state_channel.wait_message():
            state_data = await state_channel.get_json()
            exchange_rates = state_data.get(api.name.lower(), {}).get(api.schema, {})
            api.partial_state_data[self.subscription].update({'exchange_rates': exchange_rates})

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.subscribe_exchange_rates(api)))
        exchange_rates = await api.storage.get(StateStorageKey.exchange_rates, exchange=api.name, schema=api.schema)
        return {'exchange_rates': exchange_rates}


class BinanceOrderSubscriber(BinanceSubscriber):
    subscription = "order"
    subscriptions = ()


class BinancePositionSubscriber(BinanceSubscriber):
    subscription = "position"
    subscriptions = ("!ticker@arr",)
    detail_subscribe_available = False

    async def subscribe_positions_state(self, api: BinanceWssApi):
        redis = await api.storage.get_client()
        state_channel = (await redis.psubscribe(
            f"{StateStorageKey.state}:{self.subscription}.{api.account_id}.{api.name}.{api.schema}.*".lower()))[0]
        api.partial_state_data[self.subscription].setdefault('position_state', {})
        while await state_channel.wait_message():
            try:
                state_key, state_data = await state_channel.get_json()
            except ValueError:
                continue
            if (action := state_data.get('action')) and (symbol := state_data.get('symbol')):
                _state = api.partial_state_data[self.subscription]['position_state']
                if action == 'delete':
                    _state.pop(symbol.lower(), None)
                else:
                    _state[symbol.lower()] = state_data

    async def subscribe_exchange_rates(self, api: BinanceWssApi):
        redis = await api.storage.get_client()
        state_channel = (await redis.subscribe(StateStorageKey.exchange_rates))[0]
        while await state_channel.wait_message():
            state_data = await state_channel.get_json()
            exchange_rates = state_data.get(api.name.lower(), {}).get(api.schema, {})
            api.partial_state_data[self.subscription].update({'exchange_rates': exchange_rates})

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.subscribe_positions_state(api)))
        api.tasks.append(asyncio.create_task(self.subscribe_exchange_rates(api)))
        positions_state_data = await api.storage.get_pattern(
            f"{StateStorageKey.state}:{self.subscription}.{api.account_id}.{api.name}.{api.schema}.*".lower()
        )
        exchange_rates = await api.storage.get(StateStorageKey.exchange_rates, exchange=api.name, schema=api.schema)
        return {
            'position_state': utils.load_positions_state(positions_state_data),
            'exchange_rates': exchange_rates,
        }


class BinanceFuturesPositionSubscriber(BinancePositionSubscriber):
    subscriptions = ("!markPrice@arr",)

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.subscribe_exchange_rates(api)))
        async with AsyncClient(
                api_key=api.auth.get('api_key'), api_secret=api.auth.get('api_secret'), testnet=api.test
        ) as client:
            try:
                exchange_rates = await api.storage.get(StateStorageKey.exchange_rates, exchange=api.name, schema=api.schema)
                account_info = await client.futures_account_v2()
                leverage_brackets = await client.futures_leverage_bracket()
                return {
                    'position_state': utils.load_futures_positions_state(account_info),
                    'leverage_brackets': utils.load_leverage_brackets_as_dict(leverage_brackets),
                    'exchange_rates': exchange_rates,
                }
            except Exception as e:
                raise QueryError(f"Init partial state error: {e}")


class BinanceFuturesCoinPositionSubscriber(BinanceFuturesPositionSubscriber):

    async def request_positions(self, api: BinanceWssApi):
        while True:
            await self.send_request(cmd_request, api, self.subscription)
            await asyncio.sleep(10)

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.request_positions(api)))
        api.tasks.append(asyncio.create_task(self.subscribe_exchange_rates(api)))
        async with AsyncClient(
            api_key=api.auth.get('api_key'), api_secret=api.auth.get('api_secret'), testnet=api.test
        ) as client:
            try:
                account_info = await client.futures_coin_account()
                state_data = await api.storage.get(StateStorageKey.symbol, api.name, api.schema)
                leverage_brackets = await client.futures_coin_leverage_bracket()
                exchange_rates = await api.storage.get(StateStorageKey.exchange_rates, exchange=api.name, schema=api.schema)
                return {
                    'position_state': utils.load_futures_coin_positions_state(account_info, state_data),
                    'leverage_brackets': utils.load_leverage_brackets_as_dict(leverage_brackets),
                    'exchange_rates': exchange_rates,
                }
            except Exception as e:
                raise QueryError(f"Init partial state error: {e}")
