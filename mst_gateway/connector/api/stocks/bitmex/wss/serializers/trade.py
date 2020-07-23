from __future__ import annotations
from .base import BitmexSerializer
from ...utils import load_trade_data


class BitmexTradeSerializer(BitmexSerializer):
    subscription = "trade"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message['table'] == "trade"

    def _load_data(self, message: dict, item: dict) -> dict:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower(), dict())
        return load_trade_data(item, state_data)
