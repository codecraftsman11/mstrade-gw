from __future__ import annotations
from typing import Optional
from mst_gateway.connector.api.wss import StockWssApi
from mst_gateway.connector.api.stocks.binance import utils
from .base import BinanceSerializer


class BinanceSymbolSerializer(BinanceSerializer):
    subscription = "symbol"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == '24hrTicker' and bool(item)

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('s'))) is None:
                return None
        return utils.load_symbol_ws_data(self._wss_api.schema, item, state_data)


class BinanceFuturesSymbolSerializer(BinanceSymbolSerializer):

    def __init__(self, wss_api: StockWssApi):
        super().__init__(wss_api)
        self._book_ticker = {}
        self._mark_prices = {}

    def prefetch(self, message: dict) -> None:
        table = message.get('table')
        if table == 'bookTicker':
            for item in message.get('data', []):
                if symbol := item.get('s', '').lower():
                    self._book_ticker[symbol] = {'a': item.get('a'), 'b': item.get('b')}
        elif table == 'markPriceUpdate':
            for item in message.get('data', []):
                if symbol := item.get('s', '').lower():
                    self._mark_prices[symbol] = utils.to_float(item.get('p'))

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        _symbol = item.get('s', '').lower()
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(_symbol)) is None:
                return None
        item.update(dict(**self._book_ticker.get(_symbol, {}), mp=self._mark_prices.get(_symbol)))
        return utils.load_futures_symbol_ws_data(self._wss_api.schema, item, state_data)
