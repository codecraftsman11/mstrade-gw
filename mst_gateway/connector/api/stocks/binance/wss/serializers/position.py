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

    @classmethod
    def _get_data_action(cls, message) -> str:
        if message.get("table") == "ACCOUNT_UPDATE":
            for item in message.get("data", []):
                for position in item.get("a", {}).get("P", []):
                    if (
                        position["ps"] == "BOTH" and
                        not utils.to_float(position["pa"]) and
                        item["a"].get('m') != 'MARGIN_TYPE_CHANGE'
                    ):
                        return "delete"
        return super()._get_data_action(message)

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

    def get_raw_data(self, message: dict, item: dict) -> dict:
        table = message.get("table")
        if table == "ACCOUNT_UPDATE":
            for position in item.get("a", {}).get("P", []):
                if position["ps"] == "BOTH":
                    raw_data = copy(position)
                    raw_data["E"] = item.get("E")
                    for balance in item.get("a", {}).get("B", []):
                        if balance["a"] == "USDT":
                            raw_data.update(balance)
                    return raw_data
        if message.get("table") == "ACCOUNT_CONFIG_UPDATE":
            if item.get("ac", {}).get("s"):
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
        symbol_state = symbols_state.get(symbol)
        if not symbol_state:
            return None
        account_id = self._wss_api.account_id
        exchange = self._wss_api.name
        schema = self._wss_api.schema
        all_positions_state = self._wss_api.storage.get_pattern(
            f"{self.subscription}.{account_id}.{exchange}.{schema}.*".lower()
        ) or {}
        position_state = all_positions_state.pop(
            f"{self.subscription}.{account_id}.{exchange}.{schema}.{symbol}".lower(),
            None,
        )
        if raw_data.get("l") is None:
            if position_state:
                raw_data["l"] = position_state["leverage"]
            else:
                raw_data["l"] = self.leverages.get(symbol.lower())
        other_positions_state = all_positions_state
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
            raw_data["liquidation_price"] = state[0]["liquidation_price"]
        return utils.load_futures_position_ws_data(
            raw_data, self.mark_prices, symbols_state, other_positions_state
        )
