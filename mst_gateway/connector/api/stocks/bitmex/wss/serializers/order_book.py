from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set
from .base import BitmexSerializer
from ...utils import load_order_book_data

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexOrderBookSerializer(BitmexSerializer):
    subscription = "order_book"

    def __init__(self, wss_api: BitmexWssApi):
        self._symbols: Set = set()
        super().__init__(wss_api)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    def _load_data(self, message: dict, item: dict) -> dict:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower(), dict())
        data = load_order_book_data(item, state_data)
        if message['action'] in ("partial", "insert"):
            return data
        return {k: v for k, v in data.items() if v is not None}
