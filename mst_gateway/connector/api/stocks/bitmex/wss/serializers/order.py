from .base import BitmexSerializer
from ...utils import load_order_data


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 'price' in item

    def _load_data(self, message: dict, item: dict) -> dict:
        return load_order_data(item)
