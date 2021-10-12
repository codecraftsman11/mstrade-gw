from __future__ import annotations
from typing import Optional
from .base import BitmexSerializer
from ...utils import load_ws_order_book_data
from mst_gateway.connector.api.wss import StockWssApi


class BitmexOrderBookSerializer(BitmexSerializer):
    subscription = "order_book"

    def __init__(self, wss_api: StockWssApi):
        super().__init__(wss_api)
        self._order_book_ids = {}

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        symbol = item.get('symbol')
        action = message.get('action')
        self._order_book_ids.setdefault(symbol, {})
        self._add_to_order_book_ids(action, symbol, item)
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(symbol)) is None:
                return None
        data = load_ws_order_book_data(item, state_data, self._order_book_ids)
        self._del_from_order_book_ids(action, symbol, item)
        return data

    def _add_to_order_book_ids(self, action, symbol, item):
        if action in ('partial', 'insert'):
            self._order_book_ids[symbol][item.get('id')] = item.get('price')

    def _del_from_order_book_ids(self, action, symbol, item):
        if action == 'delete':
            self._order_book_ids.get(symbol, {}).pop(item.get('id'))

    def state(self, symbol: str = None) -> Optional[dict]:
        return None
