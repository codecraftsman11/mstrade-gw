from __future__ import annotations
from typing import Optional
from mst_gateway.connector.api.wss import StockWssApi
from .base import BinanceSerializer
from ...utils import load_symbol_ws_data


class BinanceSymbolSerializer(BinanceSerializer):
    subscription = "symbol"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == '24hrTicker' and bool(item)

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item.get('s', '').lower())
        if not state_data:
            return None
        return load_symbol_ws_data(item, state_data)


class BinanceFuturesSymbolSerializer(BinanceSymbolSerializer):

    def __init__(self, wss_api: StockWssApi):
        super().__init__(wss_api)
        self._book_ticker = {}

    def prefetch(self, message: dict) -> None:
        if message.get('table') != 'bookTicker':
            return None
        for item in message.get('data', []):
            if {'s', 'a', 'b'} <= item.keys():
                self._book_ticker[item['s'].lower()] = {'a': item['a'], 'b': item['b']}

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        _symbol = item.get('s', '').lower()
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(_symbol)
        if not state_data:
            return None
        item.update(**self._book_ticker.get(_symbol, {}))
        return load_symbol_ws_data(item, state_data)
