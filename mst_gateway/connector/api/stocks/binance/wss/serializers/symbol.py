from __future__ import annotations
from typing import Union
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

    def _load_data(self, message: dict, item: dict = None) -> list:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        )
        if isinstance(item, list):
            return [load_symbol_ws_data(itm, state_data.get(itm['s'].lower(), dict())) for itm in item]
        return [load_symbol_ws_data(item, state_data.get(item['s'].lower(), dict()))]
