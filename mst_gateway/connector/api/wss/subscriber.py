from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import StockWssApi


class Subscriber:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def subscribe(self, api: StockWssApi, symbol=None):
        return self._subscribe(api, symbol)

    def unsubscribe(self, api: StockWssApi, symbol=None):
        return self._unsubscribe(api, symbol)

    @abstractmethod
    def _subscribe(self, api: StockWssApi, symbol=None):
        pass

    @abstractmethod
    def _unsubscribe(self, api: StockWssApi, symbol=None):
        pass
