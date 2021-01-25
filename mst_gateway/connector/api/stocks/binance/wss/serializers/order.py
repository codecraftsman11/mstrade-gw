from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ... import utils


class BinanceOrderSerializer(BinanceSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 's' in item

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.get_state_data(item.get('s'))
        if not state_data:
            return None
        return utils.load_order_ws_data(item, state_data)
