from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set, Optional
from mst_gateway.connector import api
from .base import BinanceSerializer
from ...utils import load_order_book_ws_data

if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinanceOrderBookSerializer(BinanceSerializer):
    subscription = "order_book"

    def __init__(self, wss_api: BinanceWssApi):
        self._symbols: Set = set()
        super().__init__(wss_api)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return 's' in item

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['s'].lower())
        if not state_data:
            return None
        if 'b' in item:
            order, side = item['b'], api.BUY
        elif 'a' in item:
            order, side = item['a'], api.SELL
        else:
            return None
        return load_order_book_ws_data(item, order, side, state_data)
