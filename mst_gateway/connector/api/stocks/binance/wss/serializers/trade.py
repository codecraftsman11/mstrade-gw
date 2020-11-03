from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...utils import load_trade_ws_data


class BinanceTradeSerializer(BinanceSerializer):
    subscription = "trade"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return bool(item)

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.get_state_data(item.get('s'))
        if not state_data:
            return None
        return load_trade_ws_data(item, state_data)
