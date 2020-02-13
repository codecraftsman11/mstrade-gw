from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Tuple
from abc import ABCMeta
from abc import abstractmethod

if TYPE_CHECKING:
    from . import StockWssApi


class Serializer:
    __metaclass__ = ABCMeta
    subscription = "base"

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api
        self._state = None

    @abstractmethod
    def _get_data(self, message) -> Tuple[str, dict]:
        return None

    def _get_state(self, symbol: str = None) -> dict:
        if self._state is None:
            return None
        if symbol is None:
            return [self._state[k] for k in self._state]
        if symbol.lower() in self._state:
            return [self._state[symbol.lower()]]
        return None

    def _update_state(self, symbol: str, data: any):
        if self._state is None:
            self._state = dict()
        self._state[symbol.lower()] = data

    def data(self, message) -> dict:
        (action, data) = self._get_data(message)
        if data is None:
            return None
        return {
            'account': f"{self._wss_api}",
            'table': self.__class__.subscription,
            'action': action,
            'data': data
        }

    def state(self, symbol: str = None) -> dict:
        data = self._get_state(symbol)
        if data is None:
            return None
        return {
            'account': f"{self._wss_api}",
            'table': self.__class__.subscription,
            'action': "partial",
            'data': data
        }
