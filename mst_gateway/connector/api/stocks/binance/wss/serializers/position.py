from __future__ import annotations
from copy import copy
from typing import Optional
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import (
    BinanceSerializer,
)


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    def __init__(self, wss_api):
        super().__init__(wss_api)
        self.mark_prices = {}
        self.leverages = {}

    def prefetch(self, message: dict) -> None:
        if message.get("table") == "markPriceUpdate":
            for item in message.get("data", []):
                self.mark_prices[item["s"].lower()] = utils.to_float(item["p"])
        if message.get("table") == "ACCOUNT_CONFIG_UPDATE":
            for item in message.get("data", []):
                if item.get("ac", {}).get("s"):
                    self.leverages[item["ac"]["s"].lower()] = item["ac"].get("l")

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if (
            message["table"] in ("ACCOUNT_UPDATE", "ACCOUNT_CONFIG_UPDATE")
            and self.subscription in self._wss_api.subscriptions
        ):
            return True
        return False

    def is_state_exists(self, symbol: str) -> bool:
        state = self._get_state(symbol.lower())
        return bool(state and state[0]["volume"])

    def get_raw_data(self, message: dict, item: dict) -> dict:
        table = message.get("table")
        if table == "ACCOUNT_UPDATE":
            for p in item.get("a", {}).get("P", []):
                if p["ps"] == "BOTH":
                    raw_data = copy(p)
                    raw_data["E"] = item.get("E")
                    for b in item.get("a", {}).get("B", []):
                        if b["a"] == "USDT":
                            raw_data.update(b)
                    return raw_data
        if message.get("table") == "ACCOUNT_CONFIG_UPDATE":
            if item.get("ac", {}).get("s"):
                if self.is_state_exists(symbol=item["ac"]["s"]):
                    raw_data = item["ac"]
                    raw_data["E"] = item.get("E")
                    return raw_data
        return {}

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        raw_data = self.get_raw_data(message, item)
        if not raw_data:
            return None
        symbol = raw_data["s"].lower()
        symbols_state = self._wss_api.state_data
        if not symbols_state.get(symbol):
            return None
        account_id = self._wss_api.account_id
        other_positions_state = self._wss_api.storage.get_pattern(
            f"{self.subscription}.{account_id}.{self._wss_api.schema}.*"
        )
        if other_positions_state:
            other_positions_state.pop(
                f"{self.subscription}.{account_id}.{self._wss_api.schema}.{symbol}",
                None,
            )
        state = self._get_state(symbol)
        if state:
            if raw_data.get("pa") is None:
                raw_data["pa"] = state[0]["volume"]
            if raw_data.get("ep") is None:
                raw_data["ep"] = state[0]["entry_price"]
            if raw_data.get("up") is None:
                raw_data["up"] = state[0]["unrealised_pnl"]
            if raw_data.get("mt") is None:
                raw_data["mt"] = state[0]["leverage_type"]
            if raw_data.get("l") is None:
                raw_data["l"] = state[0]["leverage"]
            if raw_data.get("iw") is None or raw_data.get("cw") is None:
                raw_data["liquidation_price"] = state[0]["liquidation_price"]
        return utils.load_futures_position_ws_data(
            account_id, self.mark_prices, self.leverages, raw_data, symbols_state,
            other_positions_state,
        )
