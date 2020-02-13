from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional
)
from abc import (
    ABCMeta,
    abstractmethod
)
from .serializer import Serializer


if TYPE_CHECKING:
    from . import StockWssApi


class Router:
    __metaclass__ = ABCMeta

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api
        self._routed_data = None

    def get_data(self, message: str) -> Dict[str, Dict]:
        data = {}
        serializers = self._get_serializers(message)
        for subscr_name in serializers:
            data[subscr_name] = (serializers[subscr_name]
                                 .data(self._routed_data[subscr_name]))
        return data

    def get_state(self, subscr_name: str, symbol: str = None) -> Optional[dict]:
        serializer: Serializer = self._subscr_serializer(subscr_name)
        if not serializer:
            return None
        return serializer.state(symbol)

    @abstractmethod
    def _get_serializers(self, message: str) -> Dict[str, Serializer]:
        pass

    @abstractmethod
    def _subscr_serializer(self, subscr_name: str) -> Serializer:
        pass
