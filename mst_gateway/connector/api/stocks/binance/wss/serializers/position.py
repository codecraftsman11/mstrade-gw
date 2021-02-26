from __future__ import annotations
from copy import deepcopy
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
            message["table"] == "ACCOUNT_UPDATE"
            and self.subscription in self._wss_api.subscriptions
            and self.get_raw_data(message, item)
        ):
            return True
        return False

    def get_raw_data(self, message: dict, item: dict):
        table = message.get("table")
        if table == "ACCOUNT_UPDATE":
            for p in item.get("a", {}).get("P", []):
                if p["ps"] == "BOTH":
                    data = deepcopy(p)
                    for b in item.get("a", {}).get("B", []):
                        if b["a"] == "USDT":
                            data.update(b)
                    return dict(
                        **data, E=item.get("E"), l=self.leverages.get(p["s"].lower())
                    )
        return {}

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        raw_data = self.get_raw_data(message, item)
        symbol = raw_data.get("s")
        symbols_state = self._wss_api.state_data
        if not symbols_state.get(symbol.lower()):
            return None
        positions_state = self._wss_api.storage.get_pattern(
            f"{self.subscription}.{self._wss_api.account_id}.{self._wss_api.schema}.*"
        )
        if positions_state:
            positions_state.pop(
                f"{self.subscription}.{self._wss_api.account_id}.{self._wss_api.schema}.{symbol}".lower(),
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
        return utils.load_futures_position_ws_data(
            self._wss_api.account_id, self.mark_prices,
            raw_data, symbols_state, positions_state,
        )
