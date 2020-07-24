from typing import Optional
from .base import BitmexSerializer
from ...utils import load_order_data


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 'price' in item

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower())
        if not state_data:
            return None
        return load_order_data(item, state_data)
