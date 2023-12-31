from __future__ import annotations
import asyncio
import json
from asyncio import CancelledError
from typing import TYPE_CHECKING, Optional
from websockets.exceptions import ConnectionClosedError
from mst_gateway.connector.api.types import OrderSchema
from mst_gateway.connector.api.stocks.binance.lib.exceptions import BinanceAPIException
from mst_gateway.exceptions import QueryError, GatewayError
from .. import utils
from ....wss.subscriber import Subscriber
from ......storage.var import StateStorageKey
from .utils import cmd_subscribe, cmd_unsubscribe, cmd_request
from .. import rest

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
                # TODO: support limit symbol count by exchange
                symbols = api.state_symbol_list[:900]
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
            for i in range(0, symbols_count, 200):
                await asyncio.sleep(1)
                if not api.handler or api.handler.closed:
                    return
                await api.handler.send(command(subscription, symbols[i:i+200]))
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
        redis = api.storage.get_client()
        pubsub = redis.pubsub()
        pubsub.subscribe(f"{StateStorageKey.symbol}.{api.name}.{api.schema}")
        while True:
            if api.handler and api.handler.closed:
                break
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                # TODO: support limit symbol count by exchange
                symbols = set(list(json.loads(message['data']).keys())[:900])
                unsubscribe_symbols = self._subscribed_symbols.difference(symbols)
                subscribe_symbols = symbols.difference(self._subscribed_symbols)
                for symbol in unsubscribe_symbols:
                    await asyncio.sleep(1)
                    await self._unsubscribe(api, symbol)
                for symbol in subscribe_symbols:
                    await asyncio.sleep(1)
                    await self._subscribe(api, symbol)
                self._subscribed_symbols = symbols
            await asyncio.sleep(0.5)


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


class BinanceMarginSymbolSubscriber(BinanceSymbolSubscriber):
    subscriptions = ("!ticker@arr", "!bookTicker", "!markPrice@arr")


class BinanceWalletSubscriber(BinanceSubscriber):
    subscription = "wallet"
    subscriptions = ()

    async def get_wallet_state(self, api: BinanceWssApi, client: rest.BinanceRestApi):
        schema_handlers = {
            OrderSchema.exchange: (client.handler.get_account, utils.load_ws_spot_wallet_state),
            OrderSchema.margin_cross: (client.handler.get_margin_account, utils.load_ws_margin_cross_wallet_state),
            OrderSchema.margin: (client.handler.get_futures_account, utils.load_ws_futures_wallet_state),
            OrderSchema.margin_coin: (client.handler.get_futures_coin_account, utils.load_ws_futures_coin_wallet_state)
        }
        try:
            data = client.handler.handle_response(schema_handlers[api.schema][0]())
        except (KeyError, GatewayError, BinanceAPIException):
            return {}
        return schema_handlers[api.schema][1](data)

    async def subscribe_wallet_state(self, api: BinanceWssApi, client: rest.BinanceRestApi):
        while True:
            wallet_state = await self.get_wallet_state(api, client)
            api.partial_state_data[self.subscription].update({f"{self.subscription}_state": wallet_state})
            if api.subscriptions.get(self.subscription, {}):
                message = {
                    'acc': api.account_name,
                    'tb': self.subscription,
                    'sch': api.schema,
                    'act': 'update',
                    'd': list(wallet_state.values()),
                }
                await api.send_message({self.subscription: message})
            await asyncio.sleep(30)

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        self.rest_client = rest.BinanceRestApi(auth=api.auth, test=api.test, ratelimit=api.ratelimit)
        self.rest_client.open()
        api.tasks.append(asyncio.create_task(self.subscribe_wallet_state(api, self.rest_client)))
        return {}


class BinanceWalletExtraSubscriber(BinanceSubscriber):
    subscription = "wallet_extra"
    subscriptions = ()


class BinanceMarginCrossWalletExtraSubscriber(BinanceWalletSubscriber):
    subscription = "wallet_extra"

    async def get_wallet_state(self, api: BinanceWssApi, client: rest.BinanceRestApi):
        schema_handlers = {
            OrderSchema.margin_cross: (client.handler.get_margin_account, utils.load_ws_margin_cross_wallet_extra_state)
        }
        try:
            data = client.handler.handle_response(schema_handlers[api.schema][0]())
        except (KeyError, GatewayError, BinanceAPIException):
            return {}
        return schema_handlers[api.schema][1](data)


class BinanceOrderSubscriber(BinanceSubscriber):
    subscription = "order"
    subscriptions = ()


class BinancePositionSubscriber(BinanceSubscriber):
    subscription = "position"
    subscriptions = ()


class BinanceMarginPositionSubscriber(BinancePositionSubscriber):
    subscriptions = ("!markPrice@arr",)
    detail_subscribe_available = False

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        with rest.BinanceRestApi(
                auth=api.auth, test=api.test, ratelimit=api.ratelimit
        ) as client:
            try:
                resp = client.handler.get_futures_account()
                account_info = client.handler.handle_response(resp)
                resp = client.handler.get_futures_leverage_bracket()
                leverage_brackets = client.handler.handle_response(resp)
                return {
                    'position_state': utils.load_futures_positions_state(account_info),
                    'leverage_brackets': utils.load_futures_leverage_brackets_as_dict(leverage_brackets),
                }
            except Exception as e:
                raise QueryError(f"Init partial state error: {e}")


class BinanceMarginCoinPositionSubscriber(BinanceMarginPositionSubscriber):

    async def request_positions(self, api: BinanceWssApi):
        while True:
            await self.send_request(cmd_request, api, self.subscription)
            await asyncio.sleep(10)

    async def init_partial_state(self, api: BinanceWssApi) -> dict:
        api.tasks.append(asyncio.create_task(self.request_positions(api)))
        with rest.BinanceRestApi(
                auth=api.auth, test=api.test, ratelimit=api.ratelimit
        ) as client:
            try:
                resp = client.handler.get_futures_coin_account()
                account_info = client.handler.handle_response(resp)
                resp = client.handler.get_futures_coin_leverage_bracket()
                leverage_brackets = client.handler.handle_response(resp)
                state_data = api.storage.get(f"{StateStorageKey.symbol}.{api.name}.{api.schema}")
                return {
                    'position_state': utils.load_futures_coin_positions_state(account_info, state_data),
                    'leverage_brackets': utils.load_futures_coin_leverage_brackets_as_dict(leverage_brackets),
                }
            except Exception as e:
                raise QueryError(f"Init partial state error: {e}")
