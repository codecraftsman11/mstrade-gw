import asyncio
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Dict, Optional
import websockets
from mst_gateway.storage import StateStorage
from .router import Router
from .subscriber import Subscriber
from .throttle import ThrottleWss
from .. import errors
from ..schema import AUTH_SUBSCRIPTIONS, SUBSCRIPTIONS
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
    throttle = ThrottleWss()
    storage = StateStorage()

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 throttle_rate: int = 30,
                 throttle_storage=None,
                 schema='margin1',
                 state_storage=None,
                 register_state=True):
        self.tasks = list()
        if name is not None:
            self.name = name
        self.account_name = account_name or self.name
        self._options = options or {}
        self._url = url or self.__class__.BASE_URL
        self._error = errors.ERROR_OK
        self._subscriptions = {}
        self._router = self.__class__.router_class(self)
        self._throttle_rate = throttle_rate
        self.auth_connect = False
        if throttle_storage is not None:
            self.throttle = ThrottleWss(throttle_storage)
        self.schema = schema
        if state_storage is not None:
            self.storage = StateStorage(state_storage)
        self.register_state = register_state
        super().__init__(auth, logger)

    @property
    def options(self):
        return self._options

    @property
    def subscriptions(self):
        return self._subscriptions

    def __str__(self):
        return self.name

    def get_data(self, message: str) -> Dict[str, Dict]:
        return self._router.get_data(message)

    @property
    def router(self):
        return self._router

    def get_state(self, subscr_name: str, symbol: str = None) -> dict:
        return self.router.get_state(subscr_name, symbol)

    async def subscribe(self, subscr_name: str, symbol: str = None,
                        force: bool = False) -> bool:
        if not force and self.is_registered(subscr_name, symbol):
            return True
        _subscriber = self._get_subscriber(subscr_name)
        if not _subscriber:
            self._logger.error("There is no subscriber in %s for %s", self, subscr_name)
            return False
        if not await _subscriber.subscribe(self, symbol):
            self._logger.error("Error subscribing %s to %s", self, subscr_name)
            return False
        self.register(subscr_name, symbol)
        return True

    async def unsubscribe(self, subscr_name: str, symbol: str = None) -> bool:
        if not self.is_registered(subscr_name, symbol, check_for_unsub=True):
            return True
        _subscriber = self._get_subscriber(subscr_name)
        if not _subscriber:
            self._logger.error("There is no subscriber in %s to unsubscribe"
                               " from %s", self, subscr_name)
            return False
        if not await _subscriber.unsubscribe(self, symbol):
            self._logger.error("Error unsubscribing from %s in %s", subscr_name, self)
            return False
        self.unregister(subscr_name, symbol)
        return True

    def is_registered(self, subscr_name, symbol: str = None, check_for_unsub: bool = False) -> bool:
        if not check_for_unsub:
            return (symbol and symbol.lower() in self._subscriptions.get(subscr_name.lower(), set())) \
                   or True in self._subscriptions.get(subscr_name.lower(), set())
        if symbol:
            return symbol.lower() in self._subscriptions.get(subscr_name.lower(), set())
        return True in self._subscriptions.get(subscr_name.lower(), set())

    def register(self, subscr_name, symbol: str = None):
        if not self._subscriptions.get(subscr_name.lower()):
            self._subscriptions[subscr_name.lower()] = set()
        if symbol:
            self._subscriptions[subscr_name.lower()].add(symbol.lower())
        else:
            self._subscriptions[subscr_name.lower()].add(True)

    def unregister(self, subscr_name, symbol: str = None):
        if symbol and symbol.lower() in self._subscriptions.get(subscr_name.lower(), set()):
            self._subscriptions[subscr_name.lower()].remove(symbol.lower())
        if not symbol and subscr_name.lower() in self._subscriptions \
                and True in self._subscriptions[subscr_name.lower()]:
            del self._subscriptions[subscr_name.lower()]

    async def open(self, **kwargs):
        if not self.throttle.validate(
            key=dict(name=self.name, url=self._url),
            rate=self._throttle_rate
        ):
            raise ConnectionError
        restore = kwargs.get('restore', False)
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
        for t in self.tasks:
            t.cancel()
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
                except (OSError, TypeError, ValueError):
                    continue

            if self.handler.closed:
                await asyncio.sleep(kwargs.get('countdown', 10))
                try:
                    await self.open(restore=True)
                except OSError:
                    continue
            try:
                message = await self.handler.recv()
            except websockets.exceptions.ConnectionClosed:
                continue
            await self.process_message(message, recv_callback)

    async def _restore_subscriptions(self):
        for subscr in self._subscriptions:
            if subscr in self.auth_subscribers:
                if not await self.authenticate():
                    continue
            if True in self._subscriptions[subscr]:
                await self.subscribe(subscr, force=True)
            for symbol in self._subscriptions[subscr]:
                if symbol is not True:
                    await self.subscribe(subscr, symbol, force=True)

    async def _connect(self, **kwargs):
        ws_options = kwargs.get('ws_options', dict())
        return await websockets.connect(self._url,
                                        **ws_options)

    async def close(self):
        self._subscriptions = dict()
        if not self._handler:
            return
        await self._handler.close()
        self._handler = None

    async def process_message(self, message, on_message: Optional[callable] = None):
        try:
            data = self.get_data(message)
        except Exception as exc:
            self._error = errors.ERROR_INVALID_DATA
            self._logger.error("Error validating incoming message %s; Details: %s", message, exc)
            return None
        if not data:
            return None
        if on_message:
            if asyncio.iscoroutinefunction(on_message):
                return await on_message(data)
            return on_message(data)
        return data

    def _get_subscriber(self, subscr_name: str) -> Subscriber:
        if subscr_name.lower() in self.__class__.subscribers:
            return self.__class__.subscribers[subscr_name.lower()]
        return self.__class__.auth_subscribers[subscr_name.lower()]

    @abstractmethod
    async def authenticate(self, auth: dict = None) -> bool:
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __del__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def __adel__(self):
        await self.close()
