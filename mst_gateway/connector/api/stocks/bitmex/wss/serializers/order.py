from typing import Optional
from .base import BitmexSerializer
from ...converter import BitmexOrderTypeConverter
from ...utils import load_order_ws_data


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 'price' in item

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('symbol'))) is None:
                return None
        item = BitmexOrderTypeConverter.prefetch_message_data(self._wss_api.schema, item)
        return load_order_ws_data(self._wss_api.schema, item, state_data)
