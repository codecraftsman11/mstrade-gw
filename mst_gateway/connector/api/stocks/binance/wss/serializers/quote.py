from __future__ import annotations
from typing import TYPE_CHECKING
from .base import BinanceSerializer
from ..utils import load_quote_bin_ws_data

if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinanceQuoteBinSerializer(BinanceSerializer):
    subscription = "quote_bin"

    def __init__(self, wss_api: BinanceWssApi):
        self._bins = {}
        self._initialized = False
        super().__init__(wss_api)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('e') == "kline"

    def _load_data(self, message: dict, item: dict) -> dict:
        return load_quote_bin_ws_data(item, item['s'])
