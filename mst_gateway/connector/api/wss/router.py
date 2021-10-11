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

    serializer_classes = {}

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api
        self._routed_data = None
        self._serializers = {}

    async def get_data(self, message: dict) -> dict:
        data = {}
        serializers = self._get_serializers(message)
        for subscr_name, subscr_serializer in serializers.items():
            _data = await subscr_serializer.data(self._routed_data[subscr_name])
            if _data:
                data[subscr_name] = _data
        return data

    def get_state(self, subscr_name: str, symbol: str = None) -> Optional[dict]:
        serializer: Serializer = self._subscr_serializer(subscr_name)
        if not serializer:
            return None
        return serializer.state(symbol)

    @abstractmethod
    def _get_serializers(self, message: dict) -> Dict[str, Serializer]:
        raise NotImplementedError

    def _subscr_serializer(self, subscr_name) -> Serializer:
        if subscr_name not in self._serializers:
            self._serializers[subscr_name] = self.serializer_classes[subscr_name](self._wss_api)
        return self._serializers[subscr_name]
