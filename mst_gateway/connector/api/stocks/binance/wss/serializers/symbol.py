from __future__ import annotations
from typing import Union, Optional
from mst_gateway.connector.api.wss import StockWssApi
from .base import BinanceSerializer
from ...utils import load_symbol_ws_data


class BinanceSymbolSerializer(BinanceSerializer):
    subscription = "symbol"

    def is_item_valid(self, message: Union[dict, list], item) -> bool:
        if isinstance(message, list):
            return message[0].get('e') == "24hrTicker"
        elif isinstance(message, dict):
            return message.get('e') == "24hrTicker"
        return False

    def _load_data(self, message: dict, item: Union[dict, list]) -> Optional[list]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        )
        symbols = list()
        if not isinstance(item, list):
            item = [item]
        for itm in item:
            _symbol = state_data.get(itm['s'].lower())
            if _symbol:
                symbols.append(load_symbol_ws_data(itm, _symbol))
        return symbols


class BinanceFuturesSymbolSerializer(BinanceSymbolSerializer):

    def __init__(self, wss_api: StockWssApi):
        super().__init__(wss_api)
        self._book_ticker = dict()

    def is_item_valid(self, message: Union[dict, list], item) -> bool:
        if isinstance(message, dict) and message.get('e') == 'bookTicker':
            self._update_book_ticker(message)
            return False
        return super().is_item_valid(message, item)

    def _update_book_ticker(self, message: dict):
        self._book_ticker[message.get('s', '').lower()] = {'a': message['a'], 'b': message['b']}

    def _load_data(self, message: dict, item: Union[dict, list]) -> Optional[list]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        )
        symbols = list()
        if not isinstance(item, list):
            item = [item]
        for itm in item:
            state = self._get_state(itm.get('s'))
            itm.update(**self._book_ticker.get(itm.get('s').lower(), dict()))
            if not itm.get('b') and state:
                itm['b'] = state[0]['bid_price']
            if not itm.get('a') and state:
                itm['a'] = state[0]['ask_price']

            _symbol = state_data.get(itm['s'].lower())
            if _symbol:
                symbols.append(load_symbol_ws_data(itm, _symbol))
        return symbols
