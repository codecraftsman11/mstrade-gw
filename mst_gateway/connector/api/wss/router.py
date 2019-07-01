from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABCMeta
from abc import abstractmethod
from .serializer import Serializer


if TYPE_CHECKING:
    from . import StockWssApi


class Router:
    __metaclass__ = ABCMeta

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api
        self._routed_data = None

    def get_data(self, message: str) -> dict:
        serializer: Serializer = self._get_serializer(message)
        if not serializer:
            return None
        return serializer.data(self._routed_data)

    @abstractmethod
    def _get_serializer(self, message: str) -> Serializer:
        pass
