from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .base import BitmexSerializer
from ...utils import load_trade_data


if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexTradeSerializer(BitmexSerializer):
    subscription = "trade"

    def __init__(self, wss_api: BitmexWssApi):
        super().__init__(wss_api)
        self._initialized = bool(self.subscription in self._wss_api.subscriptions)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message['table'] == "trade" and self._initialized

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('symbol'))) is None:
                return None
        return load_trade_data(item, state_data, is_iso_datetime=True)
