from __future__ import annotations
from .base import BinanceSerializer
from ..utils import load_trade_ws_data, load_symbol_ws_data


class BinanceSymbolSerializer(BinanceSerializer):
    subscription = "symbol"

    def is_item_valid(self, message: dict, item) -> bool:
        return message[0].get('e') == "24hrTicker"

    def _load_data(self, message: dict, item: dict = None) -> list:
        return [load_symbol_ws_data(itm) for itm in item]
