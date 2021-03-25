from __future__ import annotations
from copy import copy, deepcopy
from typing import Optional, Tuple
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    @classmethod
    def _get_data_action(cls, message) -> str:
        if message.get("table") == "ACCOUNT_UPDATE":
            for item in message.get("data", []):
                for position in item.get("a", {}).get("P", []):
                    position_side = position["ps"]
                    position_amount = utils.to_float(position["pa"])
                    if position_side == "BOTH" and not position_amount:
                        return "delete"
        return super()._get_data_action(message)

    def prefetch(self, message: dict) -> None:
        table = message.get("table")
        if table == "markPriceUpdate":
            for item in message.get("data", []):
                symbol = item.get("s")
                if symbol:
                    mark_price = utils.to_float(item.get("p"))
                    data = {'symbol': symbol.lower(), 'mark_price': mark_price}
                    self._wss_api.update_positions_state(data, partial=True)
        if table == "ACCOUNT_UPDATE":
            for item in message.get("data", []):
                event_reason = item.get("a", {}).get("m")
                if event_reason == "MARGIN_TYPE_CHANGE":
                    for position in item["a"].get("P", []):
                        symbol = item.get("s")
                        position_side = position.get("ps")
                        if symbol and position_side == "BOTH" and not self._wss_api.is_position_exists(symbol):
                            leverage_type = utils.load_ws_futures_position_leverage_type(position.get("mt"))
                            data = {"symbol": symbol.lower(), "leverage_type": leverage_type}
                            self._wss_api.update_positions_state(data, partial=True)
        if table == "ACCOUNT_CONFIG_UPDATE":
            for item in message.get("data", []):
                symbol = item.get("ac", {}).get("s")
                if symbol:
                    leverage = utils.to_float(item["ac"].get("l"))
                    data = {'symbol': symbol.lower(), 'leverage': leverage}
                    self._wss_api.update_positions_state(data, partial=True)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if (
            message["table"] in ("ACCOUNT_UPDATE", "ACCOUNT_CONFIG_UPDATE", "markPriceUpdate")
            and self.subscription in self._wss_api.subscriptions
        ):
            return True
        return False

    def get_raw_data(self, message: dict, item: dict) -> dict:
        table = message.get("table")
        if table == "markPriceUpdate":
            symbol = item.get("s")
            if symbol and self._wss_api.is_position_exists(symbol):
                raw_data = copy(item)
                return raw_data
        if table == "ACCOUNT_UPDATE":
            for position in item.get("a", {}).get("P", []):
                symbol = position.get("s")
                position_side = position.get("ps")
                if symbol and position_side == "BOTH":
                    event_reason = item.get("a", {}).get("m")
                    if (
                        event_reason != "MARGIN_TYPE_CHANGE" or
                        event_reason == "MARGIN_TYPE_CHANGE" and
                        self._wss_api.is_position_exists(symbol)
                    ):
                        raw_data = copy(position)
                        raw_data["E"] = item.get("E")
                        for balance in item.get("a", {}).get("B", []):
                            balance_asset = balance.get("a")
                            if balance_asset == "USDT":
                                raw_data.update(balance)
                        return raw_data
        if table == "ACCOUNT_CONFIG_UPDATE":
            symbol = item.get("ac", {}).get("s")
            if symbol and self._wss_api.is_position_exists(symbol):
                raw_data = copy(item["ac"])
                raw_data["E"] = item.get("E")
                return raw_data
        return {}

    def split_positions_state(self, symbol: str) -> Tuple[dict, dict]:
        all_positions_state = deepcopy(self._wss_api.positions_state)
        position_state = all_positions_state.pop(symbol.lower(), {})
        other_positions_state = all_positions_state
        return position_state, other_positions_state

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
        position_state, other_positions_state = self.split_positions_state(symbol)
        if raw_data.get("pa") is None:
            raw_data["pa"] = position_state.get("volume")
            raw_data["side"] = position_state.get("side")
        if raw_data.get("p") is None:
            raw_data["p"] = position_state.get("mark_price")
        if raw_data.get("ep") is None:
            raw_data["ep"] = position_state.get("entry_price")
        if raw_data.get("mt") is None:
            raw_data["mt"] = position_state.get("leverage_type")
        if raw_data.get("l") is None:
            raw_data["l"] = position_state.get("leverage")
        if raw_data.get("iw") is None:
            raw_data["iw"] = position_state.get("isolated_wallet_balance")
        if raw_data.get("cw") is None:
            raw_data["cw"] = position_state.get("cross_wallet_balance")
        response = utils.load_futures_position_ws_data(raw_data, symbols_state, other_positions_state)
        position_data = copy(response)
        position_data.update({"isolated_wallet_balance": raw_data["iw"], "cross_wallet_balance": raw_data["cw"]})
        self._wss_api.update_positions_state(position_data)
        return response
