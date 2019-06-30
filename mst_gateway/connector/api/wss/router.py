from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABCMeta
from abc import abstractmethod
from .serializer import Serializer


if TYPE_CHECKING:
    from . import StockWssApi


class Router:
    __metaclass__ = ABCMeta

    def get_data(self, wss_api: StockWssApi, message: str) -> dict:
        serializer: Serializer = self._get_serializer(wss_api, message)
        if not serializer:
            return None
        if not serializer.is_valid():
            raise ValueError()
        return serializer.validated_data

    @abstractmethod
    def _get_serializer(self, wss_api: StockWssApi, message: str) -> Serializer:
        return Serializer(wss_api, message)
