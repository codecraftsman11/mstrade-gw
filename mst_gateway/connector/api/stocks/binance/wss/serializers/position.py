from __future__ import annotations
from typing import Optional
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import (
    BinanceSerializer,
)


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    def __init__(self, wss_api):
        self.mark_prices = {}
        self.leverages = {}
        super().__init__(wss_api)

    def prefetch(self, message: dict) -> None:
        table = message.get("table")
        if table == "markPriceUpdate":
            for item in message.get("data", []):
                if item.get("s"):
                    self.mark_prices[item["s"]] = item.get("p")
        if table == "ACCOUNT_CONFIG_UPDATE":
            for item in message.get("data", []):
                if item.get("ac", {}).get("s"):
                    self.leverages[item["ac"]["s"]] = item["ac"].get("l")

    @staticmethod
    def select_both_sides_position_data(item: dict):
        for p in item.get("a", {}).get("P", []):
            if p.get("ps") == "BOTH":
                return p

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if message["table"] == "ACCOUNT_UPDATE" and \
                self.subscription in self._wss_api.subscriptions and \
                self.select_both_sides_position_data(item):
            return True
        return False

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        both_sides_position_data = self.select_both_sides_position_data(item)
        symbol = both_sides_position_data.get("s")
        state_data = self._wss_api.get_state_data(symbol)
        if not state_data:
            return None
        both_sides_position_data.update({
            "timestamp": item.get("E"),
            "mark_price": self.mark_prices.get(symbol),
            "leverage": self.leverages.get(symbol),
        })
        return utils.load_futures_position_ws_data(
            both_sides_position_data, state_data
        )
