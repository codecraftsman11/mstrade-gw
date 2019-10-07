from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set
from .base import BitmexSerializer
from ...utils import load_symbol_data

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexSymbolSerializer(BitmexSerializer):
    subscription = "symbol"

    def __init__(self, wss_api: BitmexWssApi):
        self._symbols: Set = set()
        super().__init__(wss_api)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if item.get('state', '').lower() == 'open':
            self._symbols.add(item['symbol'])
        elif message['action'] == 'partial' and item['symbol'] in self._symbols:
            self._symbols.remove(item['symbol'])
        return item['symbol'] in self._symbols and 'lastPrice' in item

    def _load_data(self, message: dict, item: dict) -> dict:
        state = self._get_state(item['symbol'])
        if state:
            if item.get('prevPrice24h') is None:
                item['prevPrice24h'] = state[0]['price24']
            if item.get('lastPrice') is None:
                item['lastPrice'] = state[0]['price']
        return load_symbol_data(item)
