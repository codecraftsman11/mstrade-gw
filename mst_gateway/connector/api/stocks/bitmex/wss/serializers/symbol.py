from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set, Optional
from .base import BitmexSerializer
from ...utils import load_symbol_data, stock2symbol

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexSymbolSerializer(BitmexSerializer):
    subscription = "symbol"

    def __init__(self, wss_api: BitmexWssApi):
        self._symbols: Set = set()
        self._quotes = dict()
        super().__init__(wss_api)

    def prefetch(self, message: dict) -> None:
        if message.get("table") == "instrument":
            for item in message.get('data', []):
                if item.get('symbol'):
                    state = self._get_state(stock2symbol(item['symbol']))
                    if state:
                        if item.get('volume24h'):
                            state[0]['volume24h'] = item["volume24h"]
                        if item.get('lastPrice'):
                            state[0]['lastPrice'] = item["lastPrice"]
                        if item.get('prevPrice24h'):
                            state[0]['prevPrice24h'] = item["prevPrice24h"]
                        self._update_state(stock2symbol(item['symbol']), state[0])
        if message.get("table") == "quote":
            for item in message.get('data', []):
                if item.get('symbol') \
                        and item.get('askPrice') is not None \
                        and item.get('bidPrice') is not None:
                    self._quotes[stock2symbol(item['symbol'])] = {
                        'askPrice': item['askPrice'],
                        'bidPrice': item['bidPrice']
                    }

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if message.get('table') == 'quote':
            return False
        symbol = stock2symbol(item['symbol'])
        if item.get('state', '').lower() == 'open':
            self._symbols.add(symbol)
        elif message['action'] == 'partial' and symbol in self._symbols:
            self._symbols.discard(symbol)
        return symbol in self._symbols and 'lastPrice' in item

    def _key_map(self, key: str):
        _map = {
            'prevPrice24h': 'price24',
            'lastPrice': 'price',
            'tickSize': 'tick',
            'markPrice': 'mark_price',
            'askPrice': 'ask_price',
            'bidPrice': 'bid_price',
            'volume24h': 'volume24',
        }
        return _map.get(key)

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        symbol = stock2symbol(item['symbol'])
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(symbol, dict())
        if not state_data:
            return None
        state = self._get_state(symbol)
        if state:
            for k, v in item.items():
                _mapped_key = self._key_map(k)
                if v is None and _mapped_key:
                    item[k] = state[0][_mapped_key]
        item.update(**self._quotes.get(symbol, {}))
        return load_symbol_data(item, state_data, is_iso_datetime=True)
