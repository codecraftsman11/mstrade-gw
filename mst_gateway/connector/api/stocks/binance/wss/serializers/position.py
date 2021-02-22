from __future__ import annotations
from typing import Optional
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import (
    BinanceSerializer,
)


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if message["table"] in (
            "ACCOUNT_UPDATE", "ACCOUNT_CONFIG_UPDATE", "markPriceUpdate"
        ) and self.subscription in self._wss_api.subscriptions:
            return True
        return False

    @staticmethod
    def select_raw_data(message: dict, item: dict):
        table = message.get("table")
        if table == "markPriceUpdate":
            return dict(**item)
        if table == "ACCOUNT_UPDATE":
            for p in item.get("a", {}).get("P", []):
                if p.get("ps") == "BOTH":
                    return dict(**p, E=item.get("E"))
        if table == "ACCOUNT_CONFIG_UPDATE":
            return dict(**item.get("ac"), E=item.get("E"))
        return {}

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        raw_data = self.select_raw_data(message, item)
        symbol = raw_data.get("s")
        state_data = self._wss_api.get_state_data(symbol)
        if not state_data:
            return None
        state = self._get_state(symbol)
        if state:
            if raw_data.get('pa') is None:
                raw_data['pa'] = state[0]['volume']
            if raw_data.get('ep') is None:
                raw_data['ep'] = state[0]['entry_price']
            if raw_data.get('p') is None:
                raw_data['p'] = state[0]['mark_price']
            if raw_data.get('up') is None:
                raw_data['up'] = state[0]['unrealised_pnl']
            if raw_data.get('mt') is None:
                raw_data['mt'] = state[0]['leverage_type']
            if raw_data.get('l') is None:
                raw_data['l'] = state[0]['leverage']
        return utils.load_futures_position_ws_data(raw_data, state_data)
