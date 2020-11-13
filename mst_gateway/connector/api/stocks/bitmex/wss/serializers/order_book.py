from __future__ import annotations
from typing import Optional
from .base import BitmexSerializer
from ...utils import load_order_book_data


class BitmexOrderBookSerializer(BitmexSerializer):
    subscription = "order_book"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.get_state_data(item.get('symbol'))
        if not state_data:
            return None
        data = load_order_book_data(item, state_data)
        if message['action'] in ("partial", "insert"):
            return data
        return {k: v for k, v in data.items() if v is not None}
