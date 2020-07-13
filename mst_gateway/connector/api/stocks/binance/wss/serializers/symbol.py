from __future__ import annotations
from typing import Union
from .base import BinanceSerializer
from ..utils import load_symbol_ws_data


class BinanceSymbolSerializer(BinanceSerializer):
    subscription = "symbol"

    def is_item_valid(self, message: Union[dict, list], item) -> bool:
        if isinstance(message, list):
            return message[0].get('e') == "24hrTicker"
        elif isinstance(message, dict):
            return message.get('e') == "24hrTicker"
        return False

    def _load_data(self, message: dict, item: dict = None) -> list:
        if isinstance(item, list):
            return [load_symbol_ws_data(itm) for itm in item]
        return [load_symbol_ws_data(item)]
