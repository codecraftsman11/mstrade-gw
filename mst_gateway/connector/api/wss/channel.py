from typing import Callable, Dict, Set
from logging import Logger
from . import StockWssConnector


StockHandler = Callable[[Dict], None]


class StockWssChannel:

    def __init__(self, wss: StockWssConnector, channel: str, logger: Logger):
        self._handlers: Dict[str, Set[StockHandler]] = {}
        self._logger: Logger = logger
        self._wss: StockWssConnector = wss
        self._channel = channel

    def subscribe(self, key, handler: StockHandler):
        self._wss.subscribe(self._channel, key, self)
        if key not in self._handlers:
            self._handlers[key] = set()
        self._handlers[key].add(handler)

    def handle(self, key, data):
        if key not in self._handlers:
            return
        for _handler in self._handlers[key]:
            _handler(data)

    def unsubscribe(self):
        self._wss.unsubscribe(self._channel)
        self._handlers = {}

    @property
    def subscribed(self, key, handler):
        if key not in self._handlers:
            return False
        if handler not in self._handlers[key]:
            return False
        return True
