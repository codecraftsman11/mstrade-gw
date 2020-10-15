from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...utils import load_quote_bin_ws_data


class BinanceQuoteBinSerializer(BinanceSerializer):
    subscription = "quote_bin"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return bool(item)

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item.get('s', '').lower())
        if not state_data:
            return None
        return load_quote_bin_ws_data(item, state_data)
