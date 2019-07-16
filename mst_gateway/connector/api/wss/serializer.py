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
        self._state = dict()

    @abstractmethod
    def _get_data(self, message) -> Tuple[str, dict]:
        return None

    def _get_state(self, symbol: str = None) -> dict:
        if symbol is None:
            return [self._state[k] for k in self._state]
        if symbol in self._state:
            return [self._state[symbol]]
        return None

    def _update_state(self, symbol: str, data: any):
        self._state[symbol] = data

    def data(self, message):
        (data_type, data) = self._get_data(message)
        if data is None:
            return None
        return {
            'account': "{}.test".format(self._wss_api),
            'table': self.__class__.subscription,
            'type': data_type,
            'data': data
        }

    def state(self, symbol: str = None):
        data = self._get_state(symbol)
        if data is None:
            return None
        return {
            'account': "{}.test".format(self._wss_api),
            'table': self.__class__.subscription,
            'type': "partial",
            'data': data
        }
