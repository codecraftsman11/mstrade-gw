from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...utils import load_trade_ws_data


class BinanceTradeSerializer(BinanceSerializer):
    subscription = "trade"

    def is_item_valid(self, message: dict, item) -> bool:
        return message.get('e') == "trade"

    def _load_data(self, message: dict, item: dict = None) -> Optional[dict]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['s'].lower())
        if not state_data:
            return None
        return load_trade_ws_data(item, state_data)