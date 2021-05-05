from __future__ import annotations
from copy import deepcopy
from typing import Optional, TYPE_CHECKING
from mst_gateway.connector.api.types import OrderSchema
from .base import BinanceSerializer
from ... import utils

if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinanceWalletSerializer(BinanceSerializer):
    subscription = "wallet"

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self._initialized = bool(self.subscription in self._wss_api.subscriptions)
        self.currency_state = wss_api.partial_state_data[self.subscription].get('currency_state', {})

    def is_item_valid(self, message: dict, item) -> bool:
        return self._initialized and message['table'] == 'outboundAccountPosition'

    def filter_balances(self, item) -> dict:
        filtered = deepcopy(item)
        _balances = []
        for b in item['a'].get('B', []):
            if b['a'].lower() in self._wss_api.subscriptions[self.subscription]:
                _balances.append(b)
        filtered['a']['B'] = _balances
        return filtered

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := await self._wss_api.storage.get(
                    f'{self.subscription}.{self._wss_api.account_id}', schema=self._wss_api.schema)) is None:
                return None
        if "*" in self._wss_api.subscriptions.get(self.subscription, {}):
            if not self.currency_state:
                return None
            return self._wallet_list(item, state_data, self.currency_state)
        else:
            item = self.filter_balances(item)
            return self._wallet_detail(item, state_data)

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        if self._wss_api.schema == OrderSchema.exchange:
            fields = ('balance',)
            return utils.ws_spot_wallet(item, state_data, currencies, assets, fields)
        elif self._wss_api.schema == OrderSchema.margin2:
            fields = ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed')
            return utils.ws_margin_wallet(item, state_data, currencies, assets, fields)

    def _wallet_detail(self, item, state_data):
        _state_balances = state_data.pop('balances', {})
        if self._wss_api.schema == OrderSchema.exchange:
            return dict(balances=utils.ws_spot_balance_data(item.get('B'), _state_balances))
        elif self._wss_api.schema == OrderSchema.margin2:
            return dict(balances=utils.ws_margin_balance_data(item.get('B'), _state_balances))

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_data(data, valid_item)


class BinanceFuturesWalletSerializer(BinanceWalletSerializer):

    def is_item_valid(self, message: dict, item) -> bool:
        return self._initialized and message['table'] == 'ACCOUNT_UPDATE'

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        fields = ('balance', 'unrealised_pnl', 'margin_balance')
        return utils.ws_futures_wallet(item, state_data, currencies, assets, fields)

    def _wallet_detail(self, item, state_data):
        balances = item['a']['B']
        _state_balances = state_data.pop('balances', {})
        return dict(
            balances=utils.ws_futures_balance_data(balances, item['a'].get('P', []), _state_balances)
        )
