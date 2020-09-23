from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set, Optional
from .base import BitmexSerializer
from ...utils import load_symbol_data

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexSymbolSerializer(BitmexSerializer):
    subscription = "symbol"

    def __init__(self, wss_api: BitmexWssApi):
        self._symbols: Set = set()
        self._quotes = dict()
        super().__init__(wss_api)

    def prefetch(self, message: dict) -> None:
        for item in message.get('data', []):
            if item.get('symbol') \
                    and item.get('askPrice') is not None \
                    and item.get('bidPrice') is not None:
                self._quotes[item['symbol'].lower()] = {
                    'askPrice': item['askPrice'],
                    'bidPrice': item['bidPrice']
                }

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if message.get('table') == 'quote':
            return False
        if item.get('state', '').lower() == 'open':
            self._symbols.add(item['symbol'])
        elif message['action'] == 'partial' and item['symbol'] in self._symbols:
            self._symbols.remove(item['symbol'])
        return item['symbol'] in self._symbols and 'lastPrice' in item

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower(), dict())
        if not state_data:
            return None
        state = self._get_state(item['symbol'])
        if state:
            if item.get('prevPrice24h') is None:
                item['prevPrice24h'] = state[0]['price24']
            if item.get('lastPrice') is None:
                item['lastPrice'] = state[0]['price']
            if item.get('tickSize') is None:
                item['tickSize'] = state[0]['tick']
            if item.get('markPrice') is None:
                item['markPrice'] = state[0]['mark_price']
            if item.get('askPrice') is None:
                item['askPrice'] = state[0]['ask_price']
            if item.get('bidPrice') is None:
                item['bidPrice'] = state[0]['bid_price']
            if item.get('volume24h') is None:
                item['volume24h'] = state[0]['volume24']
        quote = self._quotes.get(item['symbol'].lower())
        if quote:
            item.update(**quote)
        return load_symbol_data(item, state_data)
