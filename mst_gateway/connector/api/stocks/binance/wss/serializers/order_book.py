from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set
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
        return message.keys() >= {'a', 'b'}

    def _load_data(self, message: dict, item: dict) -> list:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['s'].lower(), dict())
        data = list()
        bid = item.pop('b')
        ask = item.pop('a')
        data.extend([load_order_book_ws_data(item, b, api.BUY, state_data) for b in bid])
        data.extend([load_order_book_ws_data(item, a, api.SELL, state_data) for a in ask])
        return data
