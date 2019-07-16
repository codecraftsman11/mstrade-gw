from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Tuple
from abc import ABCMeta
from abc import abstractmethod
from ....wss.serializer import Serializer
from .. import utils

if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexSerializer(Serializer):
    __metaclass__ = ABCMeta
    subscription = "base"

    @abstractmethod
    def _load_data(self, table: str, item: dict) -> dict:
        return item

    @abstractmethod
    def is_item_valid(self, table: str, item: dict) -> bool:
        return False

    def _get_data(self, message) -> Tuple[str, dict]:
        data = []
        for item in message['data']:
            new_state = self._load_data(message['table'], item)
            self._update_state(new_state['symbol'], new_state)
            data.append(new_state)
        print(message)
        if message.get('action') == "partial":
            data_type = "partial"
        else:
            data_type = "update"
        return (data_type, data)


class BitmexSymbolSerializer(BitmexSerializer):
    subscription = "symbol"

    def is_item_valid(self, table: str, item: dict) -> bool:
        return 'lastPrice' in item

    def _load_data(self, table: str, item: dict):
        return utils.load_symbol_data(item)


class BitmexQuoteBinSerializer(BitmexSerializer):
    subscription = "quote_bin"

    def __init__(self, wss_api: BitmexWssApi):
        self._bins = {}
        super().__init__(wss_api)

    def is_item_valid(self, table: str, item: dict) -> bool:
        if table in ("trade", "tradeBin1m"):
            return True
        return False

    def _load_data(self, table: str, item: dict) -> dict:
        if table == "tradeBin1m":
            return self._reset_quote_bin(item)
        return self._update_quote_bin(item)

    def _update_quote_bin(self, item):
        quote = utils.load_quote_data(item)
        quote_bin = self._bins.get(item['symbol'])
        if not quote_bin:
            quote_bin = {
                'symbol': quote['symbol'],
                'timestamp': quote['timestamp'],
                'open': quote['price'],
                'close': quote['price'],
                'high': quote['price'],
                'low': quote['price'],
                'volume': quote['volume']
            }
        else:
            quote_bin['timestamp'] = quote['timestamp']
            quote_bin['close'] = quote['price']
            quote_bin['high'] = max(quote_bin['high'], quote['price'])
            quote_bin['low'] = min(quote_bin['low'], quote['price'])
            quote_bin['volume'] += quote['volume']

        self._bins[item['symbol']] = quote_bin
        return quote_bin

    def _reset_quote_bin(self, item):
        self._bins[item['symbol']] = None
        return utils.load_quote_bin_data(item)


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    def is_item_valid(self, table: str, item: dict) -> bool:
        return 'price' in item

    def _load_data(self, table: str, item: dict) -> dict:
        return utils.load_order_data(item)
