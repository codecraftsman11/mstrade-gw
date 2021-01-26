from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Set, Optional
from .base import BitmexSerializer
from ...utils import load_symbol_data, stock2symbol, to_float

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
                            state[0]['volume24'] = item['volume24h']
                        if item.get('prevPrice24h'):
                            state[0]['price24'] = to_float(item['prevPrice24h'])
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
            'price24': 'prevPrice24h',
            'tick': 'tickSize',
            'volume_tick': 'lotSize',
            'ask_price': 'askPrice',
            'bid_price': 'bidPrice',
            'volume24': 'volume24h',
        }
        return _map.get(key)

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        symbol = stock2symbol(item['symbol'])
        state_data = None
        if self._wss_api.register_state:
            if state_data := self._wss_api.get_state_data(symbol) is None:
                return None
        state = self._get_state(symbol)
        if state:
            for k, v in state[0].items():
                _mapped_key = self._key_map(k)
                if _mapped_key and item.get(_mapped_key) is None:
                    item[_mapped_key] = state[0][k]
        item.update(**self._quotes.get(symbol, {}))
        return load_symbol_data(item, state_data, is_iso_datetime=True)
