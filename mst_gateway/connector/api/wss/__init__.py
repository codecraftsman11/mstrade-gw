import asyncio
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Dict, Optional, Union
import websockets
from copy import deepcopy
from mst_gateway.storage import AsyncStateStorage
from .router import Router
from .subscriber import Subscriber
from .throttle import ThrottleWss
from .. import errors
from ..schema import AUTH_SUBSCRIPTIONS, SUBSCRIPTIONS
from ..utils import parse_message
from ...base import Connector


class StockWssApi(Connector):
    __metaclass__ = ABCMeta
    router_class = Router
    subscribers: Dict[str, Subscriber] = {key: None for key in
                                          SUBSCRIPTIONS}
    auth_subscribers: Dict[str, Subscriber] = {key: None for key in
                                               AUTH_SUBSCRIPTIONS}
    register_state_groups = []
    name = "Base"
    BASE_URL = None
    TEST_URL = None
    throttle = ThrottleWss()
    storage = AsyncStateStorage()
    partial_state_data = {}
    __state_data = {}

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 test: bool = True,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 throttle_rate: int = 30,
                 throttle_storage=None,
                 schema='margin1',
                 state_storage=None,
                 register_state=True):
        self.test = test
        self.tasks = list()
        if name is not None:
            self.name = name.lower()
        self.account_id, self.account_name = self._parse_account_name(account_name or self.name)
        self._options = options or {}
        self._url = self._load_url(url)
        self._error = errors.ERROR_OK
        self._subscriptions = {}
        self._router = self.__class__.router_class(self)
        self._throttle_rate = throttle_rate
        self.auth_connect = False
        if throttle_storage is not None:
            self.throttle = ThrottleWss(throttle_storage)
        self.schema = schema
        if state_storage is not None:
            self.storage = AsyncStateStorage(state_storage)
        self.register_state = register_state
        super().__init__(auth, logger)
        self.__init_partial_state_data()

    def _load_url(self, url):
        if self.test:
            return url or self.TEST_URL
        return url or self.BASE_URL

    @property
    def options(self):
        return self._options

    @property
    def subscriptions(self):
        return self._subscriptions

    @property
    def state_data(self):
        return self.__state_data

    def _parse_account_name(self, account_name: str):
        _split_acc = account_name.split('.')
        account_id = None
        if len(_split_acc) > 2:
            account_id = _split_acc.pop(2)
        account_name = '.'.join(_split_acc)
        return account_id, account_name

    def __str__(self):
        return self.name

    def __init_partial_state_data(self):
        for subscription in [*self.subscribers.keys(), *self.auth_subscribers.keys()]:
            self.partial_state_data.setdefault(subscription, {})

    def __del_partial_state_data(self):
        for subscription in [*self.subscribers.keys(), *self.auth_subscribers.keys()]:
            self.partial_state_data.setdefault(subscription, {}).clear()

    async def get_data(self, message: dict) -> Dict[str, Dict]:
        data = await self._router.get_data(message)
        return data

    @property
    def router(self):
        return self._router

    def get_state(self, subscr_name: str, symbol: str = None) -> dict:
        return self.router.get_state(subscr_name, symbol)

    async def subscribe(self, subscr_channel: Optional[str],  subscr_name: str, symbol: str = None,
                        force: bool = False) -> bool:
        _subscriber = self._get_subscriber(subscr_name)
        if not _subscriber:
            self._logger.error(f"There is no subscriber in {self} to subscribe for {subscr_name}")
            return False
        if force or not self.is_registered(subscr_name, symbol):
            if not await _subscriber.subscribe(self, symbol):
                self._logger.error(f"Error subscribing {self} to {subscr_name} with args {symbol}")
                return False
        if subscr_channel or not force:
            self.register(subscr_channel, subscr_name, symbol)
        return True

    async def unsubscribe(self, subscr_channel: Optional[str], subscr_name: str, symbol: str = None) -> bool:
        _subscriber = self._get_subscriber(subscr_name)
        if not _subscriber:
            self._logger.error(f"There is no subscriber in {self} to unsubscribe from {subscr_name}")
            return False
        _result, symbol = self.unregister(subscr_channel, subscr_name, symbol)
        if not self._subscriptions and _subscriber.is_close_connection:
            await self.close()
        elif _result and self.is_unregistered(subscr_name, symbol):
            if not await _subscriber.unsubscribe(self, symbol):
                self._logger.error(f"Error unsubscribing from {subscr_name} with args {symbol} in {self}")
        return True

    def is_registered(self, subscr_name, symbol: str = None) -> bool:
        subscr_name = subscr_name.lower()
        symbol = symbol.lower() if isinstance(symbol, str) else '*'
        if subscr_name not in self._subscriptions:
            return False
        if '*' in self._subscriptions[subscr_name]:
            return True
        if symbol in self._subscriptions[subscr_name]:
            return True
        return False

    def is_unregistered(self, subscr_name, symbol: str = None) -> bool:
        subscr_name = subscr_name.lower()
        symbol = symbol.lower() if isinstance(symbol, str) else '*'
        if subscr_name not in self._subscriptions:
            return True
        if symbol not in self._subscriptions[subscr_name]:
            return True
        if not self._subscriptions[subscr_name][symbol]:
            return True
        return False

    def register(self, subscr_channel: str, subscr_name, symbol: str = None):
        subscr_name = subscr_name.lower()
        symbol = symbol.lower() if isinstance(symbol, str) else '*'
        if subscr_name not in self._subscriptions:
            self._subscriptions[subscr_name] = dict()
        if '*' in self._subscriptions[subscr_name]:
            self._subscriptions[subscr_name]['*'].add(subscr_channel)
            return True, '*'
        if symbol not in self._subscriptions[subscr_name]:
            self._subscriptions[subscr_name][symbol] = {subscr_channel}
        else:
            self._subscriptions[subscr_name][symbol].add(subscr_channel)
        if symbol == '*':
            self.remap_subscriptions(subscr_name)
        return True, symbol

    def remap_subscriptions(self, subscr_name: str):
        symbols = set(self._subscriptions[subscr_name].keys())
        symbols.discard('*')
        for symbol in symbols:
            self._subscriptions[subscr_name]['*'].update(
                self._subscriptions[subscr_name].pop(symbol, set())
            )
        return None

    def unregister(self, subscr_channel: str, subscr_name: str, symbol: str = None):
        subscr_name = subscr_name.lower()
        if subscr_name not in self._subscriptions:
            return False, symbol
        if '*' in self._subscriptions[subscr_name] or symbol is None:
            symbol = '*'
        else:
            symbol = symbol.lower()
        if symbol in self._subscriptions[subscr_name]:
            _res = False
            self._subscriptions[subscr_name][symbol].discard(subscr_channel)
            if not self._subscriptions[subscr_name][symbol]:
                del self._subscriptions[subscr_name][symbol]
                _res = True
            if not self._subscriptions[subscr_name]:
                del self._subscriptions[subscr_name]
            return _res, symbol
        return False, symbol

    async def open(self, **kwargs):
        throttle_valid = await self.throttle.validate(
            key=dict(name=self.name, url=self._url),
            rate=self._throttle_rate
        )
        if not throttle_valid:
            raise ConnectionError
        restore = kwargs.get('restore', False)
        if not restore:
            self.tasks.append(asyncio.create_task(self.__load_state_data()))
        self._handler = await self._connect(**kwargs)
        if restore:
            await self._restore_subscriptions()
        return self._handler

    def create_task(self, recv_callback, **kwargs):
        _task = asyncio.create_task(
            self.consume(
                recv_callback,
                **kwargs
            )
        )
        self.tasks.append(_task)
        return _task

    def cancel_task(self):
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        return True

    def run(self, recv_callback, loop=None, **kwargs):
        if not loop:
            loop = asyncio.new_event_loop()
        loop.run_until_complete(
            self.consume(
                recv_callback,
                **kwargs
            )
        )

    async def consume(self, recv_callback: callable, **kwargs):
        while True:
            if not self.handler:
                try:
                    await self.open()
                except (OSError, TypeError, ValueError, ConnectionError):
                    continue
            if self.handler.closed:
                await asyncio.sleep(kwargs.get('countdown', 10))
                try:
                    await self.open(restore=True)
                except (OSError, ConnectionError):
                    continue
            try:
                message = await self.handler.recv()
            except websockets.exceptions.ConnectionClosed:
                continue
            await self.process_message(message, recv_callback)

    async def _restore_subscriptions(self):
        for subscr_name, value in deepcopy(self._subscriptions).items():
            if subscr_name in self.auth_subscribers:
                if not await self.authenticate():
                    del self._subscriptions[subscr_name]
                    continue
            for subscr_symbol in value:
                await self.subscribe(None, subscr_name, subscr_symbol, force=True)

    async def _connect(self, **kwargs):
        ws_options = kwargs.get('ws_options', dict())
        return await websockets.connect(self._url, **ws_options)

    async def close(self):
        self._subscriptions = {}
        self.__del_partial_state_data()
        self.cancel_task()
        if not self._handler:
            return
        await self._handler.close()
        self._handler = None

    async def process_message(self, message, on_message: Optional[callable] = None):
        response = False
        message = parse_message(message)
        if not message:
            return response
        message = self._lookup_table(message)
        if not message:
            return response
        messages = self._split_message(message)
        for message in messages:
            try:
                data = await self.get_data(message)
            except Exception as exc:
                self._error = errors.ERROR_INVALID_DATA
                self._logger.error("Error validating incoming message %s; Details: %s", message, exc)
                continue
            if not data:
                continue
            if on_message:
                if asyncio.iscoroutinefunction(on_message):
                    await on_message(data)
                else:
                    on_message(data)
                response = True
        return response

    def _get_subscriber(self, subscr_name: str) -> Optional[Subscriber]:
        subscr_name = subscr_name.lower()
        if subscr_name in self.subscribers:
            return self.subscribers[subscr_name]
        if subscr_name in self.auth_subscribers:
            return self.auth_subscribers[subscr_name]
        return None

    def _lookup_table(self, message: Union[dict, list]) -> Optional[dict]:
        if 'table' in message:
            return message
        return None

    def _split_message(self, message) -> list:
        if isinstance(message, list):
            return message
        return [message]

    @abstractmethod
    async def authenticate(self, auth: dict = None) -> bool:
        pass

    def get_state_data(self, symbol):
        if not symbol:
            return None
        return self.__state_data.get(symbol.lower())

    async def __load_state_data(self):
        self.__state_data = await self.storage.get('symbol', self.name, self.schema)
        redis = await self.storage.get_client()
        symbol_channel = (await redis.subscribe('symbol'))[0]
        while await symbol_channel.wait_message():
            symbols = await symbol_channel.get_json()
            self.__state_data = symbols.get(self.name, {}).get(self.schema, {})

    @property
    def state_symbol_list(self) -> list:
        return list(self.__state_data.keys())

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass

    def __del__(self):
        pass

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.close()

    async def __adel__(self):
        await self.close()
