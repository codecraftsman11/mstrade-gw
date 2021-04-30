from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...utils import load_trade_ws_data


class BinanceTradeSerializer(BinanceSerializer):
    subscription = "trade"

    @classmethod
    def _get_data_action(cls, message) -> str:
        return 'insert'

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return bool(item)

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('s'))) is None:
                return None
        return load_trade_ws_data(item, state_data)
