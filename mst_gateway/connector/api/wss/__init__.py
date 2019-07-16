from typing import Dict
from typing import Coroutine
import asyncio
from abc import ABCMeta
from abc import abstractmethod
from logging import Logger
import websockets
from ...base import Connector
from .. import errors
from .subscriber import Subscriber
from .router import Router
from ..schema import SUBSCRIPTIONS
from ..schema import AUTH_SUBSCRIPTIONS


class StockWssApi(Connector):
    __metaclass__ = ABCMeta
    router_class = Router
    subscribers: Dict[str, Subscriber] = {key: None for key in
                                          SUBSCRIPTIONS}
    auth_subscribers: Dict[str, Subscriber] = {key: None for key in
                                               AUTH_SUBSCRIPTIONS}
    name = "Base"
    BASE_URL = None

    def __init__(self,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None):
        self._url = url if url is not None else self.__class__.BASE_URL
        self._error = errors.ERROR_OK
        self._subscriptions = dict()
        self._router = self.__class__.router_class(self)
        super().__init__(auth, logger)

    def __str__(self):
        return "{}".format(self.__class__.name)

    def get_data(self, message: str) -> dict:
        return self.router.get_data(message)

    @property
    def router(self):
        return self._router

    def get_state(self, subscr_name: str, symbol: str = None) -> dict:
        return self.router.get_state(subscr_name, symbol)

    async def subscribe(self, subscr_name: str, symbol: str = None) -> bool:
        if self.is_registered(subscr_name, symbol):
            return True
        subscriber = self._get_subscriber(subscr_name)
        if not subscriber:
            self._logger.error("There is no subscriber in %s for %s", self, subscr_name)
            return False
        if not await subscriber.subscribe(self, symbol):
            self._logger.error("Error subscribing %s to %s", self, subscr_name)
            return False
        self.register(subscr_name, symbol)
        return True

    async def unsubscribe(self, subscr_name: str, symbol: str = None) -> bool:
        if not self.is_registered(subscr_name, symbol):
            return True
        subscriber = self._get_subscriber(subscr_name)
        if not subscriber:
            self._logger.error("There is no subscriber in %s to unsubscribe"
                               " from %s", self, subscr_name)
            return False
        if not await subscriber.unsubscribe(self, symbol):
            self._logger.error("Error unsubscribing from %s in %s", subscr_name, self)
            return False
        self.unregister(subscr_name, symbol)
        return True

    def is_registered(self, subscr_name, symbol: str = None) -> bool:
        if subscr_name not in self._subscriptions:
            return False
        if isinstance(self._subscriptions[subscr_name], bool):
            return True
        if symbol is not None and symbol in self._subscriptions[subscr_name]:
            return True
        return False

    def register(self, subscr_name, symbol: str = None):
        if symbol is None:
            self._subscriptions[subscr_name] = True
        elif subscr_name not in self._subscriptions:
            self._subscriptions[subscr_name] = {symbol: True}
        else:
            self._subscriptions[subscr_name][symbol] = True

    def unregister(self, subscr_name, symbol: str = None):
        if subscr_name not in self._subscriptions:
            return
        if symbol is None:
            del self._subscriptions[subscr_name]
            return
        if isinstance(self._subscriptions[subscr_name], dict):
            if symbol in self._subscriptions[subscr_name]:
                del self._subscriptions[subscr_name][symbol]
            if not self._subscriptions[subscr_name]:
                del self._subscriptions[subscr_name]

    async def open(self, **kwargs):
        self._handler = await self._connect(**kwargs)
        return self._handler

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

    async def process_message(self, message, on_message: Coroutine = None):
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
        if subscr_name in self.__class__.subscribers:
            return self.__class__.subscribers[subscr_name]
        return self.__class__.auth_subscribers[subscr_name]

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
