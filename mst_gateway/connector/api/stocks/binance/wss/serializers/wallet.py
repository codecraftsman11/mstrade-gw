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
        self._state_data = wss_api.partial_state_data[self.subscription]

    @property
    def exchange_rates(self):
        return self._state_data.get('exchange_rates', {})

    def is_item_valid(self, message: dict, item) -> bool:
        return message['table'] == 'outboundAccountPosition'

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
            if self._wss_api.register_state and not self.exchange_rates:
                return None
            return self._wallet_list(item, state_data, self.exchange_rates)
        else:
            item = self.filter_balances(item)
            _b = self._wallet_detail(item, state_data)
            return _b

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        if self._wss_api.schema == OrderSchema.exchange:
            fields = ('bl',)
            return utils.ws_spot_wallet(item, state_data, currencies, assets, fields, self._wss_api.schema)
        elif self._wss_api.schema == OrderSchema.margin2:
            fields = ('bl', 'upnl', 'mbl', 'bor')
            return utils.ws_margin_wallet(item, state_data, currencies, assets, fields, self._wss_api.schema)

    def _wallet_detail(self, item, state_data):
        _state_balances = state_data.pop('bls', {})
        if self._wss_api.schema == OrderSchema.exchange:
            return dict(bls=utils.ws_spot_balance_data(item.get('B'), _state_balances))
        elif self._wss_api.schema == OrderSchema.margin2:
            return dict(bls=utils.ws_margin_balance_data(item.get('B'), _state_balances))

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_data(data, valid_item)


class BinanceFuturesWalletSerializer(BinanceWalletSerializer):

    def is_item_valid(self, message: dict, item) -> bool:
        return message['table'] == 'ACCOUNT_UPDATE' and self.subscription in self._wss_api.subscriptions

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        fields = ('bl', 'upnl', 'mbl')
        return utils.ws_futures_wallet(item, state_data, currencies, assets, fields, self._wss_api.schema)

    def _wallet_detail(self, item, state_data):
        balances = item['a']['B']
        _state_balances = state_data.pop('bls', {})
        return dict(
            bls=utils.ws_futures_balance_data(balances, item['a'].get('P', []), _state_balances)
        )
