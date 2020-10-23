from typing import Optional
from .base import BitmexSerializer
from ...utils import load_order_ws_data


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 'price' in item

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.get_state_data(item.get('symbol'))
        if not state_data:
            return None
        return load_order_ws_data(item, state_data)
