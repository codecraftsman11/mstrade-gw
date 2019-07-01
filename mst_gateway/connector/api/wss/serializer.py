from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABCMeta
from abc import abstractmethod

if TYPE_CHECKING:
    from . import StockWssApi


class Serializer:
    __metaclass__ = ABCMeta
    subscription = "base"

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api

    @abstractmethod
    def _get_data(self, message) -> dict:
        return None

    def data(self, message):
        data = self._get_data(message)
        if data is None:
            return None
        return {
            'connection': str(self._wss_api),
            'account': "test",
            'table': self.__class__.subscription,
            'data': data
        }
