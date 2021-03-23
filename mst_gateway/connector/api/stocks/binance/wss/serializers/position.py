from __future__ import annotations
from copy import copy, deepcopy
from typing import Optional, Tuple
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.connector.api.stocks.binance.wss.serializers.base import BinanceSerializer


class BinanceFuturesPositionSerializer(BinanceSerializer):
    subscription = "position"

    def __init__(self, wss_api):
        super().__init__(wss_api)
        self.mark_prices = {}

        subscription = self.subscription
        account_id = self._wss_api.account_id
        exchange = self._wss_api.name
        schema = self._wss_api.schema
        positions_state_key_pattern = f"{subscription}.{account_id}.{exchange}.{schema}.*".lower()
        self.__positions_state = self._wss_api.storage.get_pattern(positions_state_key_pattern) or {}

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
        if message.get("table") == "markPriceUpdate":
            for item in message.get("data", []):
                symbol = item.get("s")
                if symbol:
                    self.mark_prices[symbol.lower()] = utils.to_float(item.get("p"))

    def is_item_valid(self, message: dict, item: dict) -> bool:
        if (
            message["table"] in ("ACCOUNT_UPDATE", "ACCOUNT_CONFIG_UPDATE", "markPriceUpdate")
            and self.subscription in self._wss_api.subscriptions
        ):
            return True
        return False

    def get_raw_data(self, message: dict, item: dict) -> dict:
        table = message.get("table")
        if message.get("table") == "markPriceUpdate":
            symbol = item.get("s")
            if symbol:
                raw_data = copy(item)
                return raw_data
        if table == "ACCOUNT_UPDATE":
            for position in item.get("a", {}).get("P", []):
                position_side = position["ps"]
                if position_side == "BOTH":
                    raw_data = copy(position)
                    raw_data["E"] = item.get("E")
                    for balance in item.get("a", {}).get("B", []):
                        balance_asset = balance["a"]
                        if balance_asset == "USDT":
                            raw_data.update(balance)
                    return raw_data
        if message.get("table") == "ACCOUNT_CONFIG_UPDATE":
            symbol = item.get("ac", {}).get("s")
            if symbol:
                raw_data = copy(item["ac"])
                raw_data["E"] = item.get("E")
                return raw_data
        return {}

    def get_position_state_key(self, symbol: str) -> str:
        subscription = self.subscription
        account_id = self._wss_api.account_id
        exchange = self._wss_api.name
        schema = self._wss_api.schema
        position_state_key = f"{subscription}.{account_id}.{exchange}.{schema}.{symbol}".lower()
        return position_state_key

    def get_position_state_data(self, data: dict) -> dict:
        position_state_data = {
            'symbol': data['symbol'].lower(),
            'side': data['side'],
            'volume': data['volume'],
            'price': data['entry_price'],
            'leverage_type': data['leverage_type'],
            'leverage': data['leverage'],
        }
        return position_state_data

    def get_positions_states(self, symbol: str) -> Tuple[dict, dict]:
        all_positions_state = deepcopy(self.__positions_state)
        position_state_key = self.get_position_state_key(symbol)
        position_state = all_positions_state.pop(position_state_key, {})
        other_positions_state = all_positions_state
        return position_state, other_positions_state

    def __update_position_state(self, position_data: dict) -> None:
        position_state_key = self.get_position_state_key(position_data["symbol"].lower())
        if position_data["volume"]:
            position_state_data = self.get_position_state_data(position_data)
            self.__positions_state[position_state_key] = position_state_data
        else:
            self.__positions_state.pop(position_state_key, None)

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
        position_state, other_positions_state = self.get_positions_states(symbol)
        if not position_state:
            return None
        if raw_data.get("iw") is None:
            raw_data['iw'] = self._wss_api.wallet_balances.get('isolated')
        if raw_data.get("cw") is None:
            raw_data['cw'] = self._wss_api.wallet_balances.get('cross')
        if raw_data.get("pa") is None:
            raw_data["pa"] = position_state["volume"]
            raw_data["side"] = position_state["side"]
        if raw_data.get("ep") is None:
            raw_data["ep"] = position_state["price"]
        if raw_data.get("mt") is None:
            raw_data["mt"] = position_state["leverage_type"]
        if raw_data.get("l") is None:
            raw_data["l"] = position_state["leverage"]
        position_data = utils.load_futures_position_ws_data(raw_data, self.mark_prices, symbols_state, other_positions_state)
        self.__update_position_state(position_data)
        wallet_balances = {'isolated': utils.to_float(raw_data.get('iw')), 'cross': utils.to_float(raw_data.get('cw'))}
        self._wss_api.update_wallet_balances(wallet_balances)
        return position_data
