from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import StockWssApi


class Serializer:
    def __init__(self, wss_api: StockWssApi, data: dict):
        self._data = data
        self._wss_api = wss_api
        self._validated_data = None

    def is_valid(self):
        self._validated_data = self._data
        return True

    @property
    def data(self):
        return self._data

    @property
    def validated_data(self):
        return self._validated_data
