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

    @property
    def wallet_state(self):
        return self._state_data.get('wallet_state', {})

    def is_item_valid(self, message: dict, item) -> bool:
        return message['table'] == 'outboundAccountPosition'

    def filter_balances(self, item) -> dict:
        filtered = deepcopy(item)
        _balances = []
        for b in item.get('B', []):
            if b['a'].lower() in self._wss_api.subscriptions[self.subscription]:
                _balances.append(b)
        filtered['B'] = _balances
        return filtered

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        if self._wss_api.register_state and not self.wallet_state:
            return None
        if "*" in self._wss_api.subscriptions.get(self.subscription, {}):
            if self._wss_api.register_state and not self.exchange_rates:
                return None
            return self._wallet_list(item)
        else:
            item = self.filter_balances(item)
            _b = self._wallet_detail(item)
            return _b

    def _wallet_list(self, item):
        assets = ('btc', 'usd')
        if self._wss_api.schema == OrderSchema.exchange:
            fields = ('bl', 'upnl', 'mbl')
            return utils.ws_spot_wallet(item, self._wss_api.schema, self.exchange_rates, fields, assets)
        elif self._wss_api.schema == OrderSchema.margin2:
            fields = ('bl', 'upnl', 'mbl')
            extra_fields = ('ist', 'bor', 'istr', 'abor')
            return utils.ws_margin_wallet(item, self._wss_api.schema, self.wallet_state, self.exchange_rates,
                                          fields, extra_fields, assets)

    def _wallet_detail(self, item):
        balances = item.get('B', [])
        if self._wss_api.schema == OrderSchema.exchange:
            return dict(bls=utils.ws_spot_balance_data(balances))
        elif self._wss_api.schema == OrderSchema.margin2:
            return dict(bls=utils.ws_margin_balance_data(balances, self.wallet_state))

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_data(data, valid_item)


class BinanceFuturesWalletSerializer(BinanceWalletSerializer):

    def filter_balances(self, item) -> dict:
        filtered = deepcopy(item)
        _balances = []
        for b in item['a'].get('B', []):
            if b['a'].lower() in self._wss_api.subscriptions[self.subscription]:
                _balances.append(b)
        filtered['a']['B'] = _balances
        return filtered

    def is_item_valid(self, message: dict, item) -> bool:
        return message['table'] == 'ACCOUNT_UPDATE' and self.subscription in self._wss_api.subscriptions

    def _wallet_list(self, item):
        assets = ('btc', 'usd')
        fields = ('bl', 'upnl', 'mbl')
        extra_fields = ('ist', 'bor')
        return utils.ws_futures_wallet(item, self._wss_api.schema, self.wallet_state, self.exchange_rates,
                                       fields, extra_fields, assets)

    def _wallet_detail(self, item):
        balances = item.get('a', {}).get('B', [])
        positions = item.get('a', {}).get('P', [])
        return dict(
            bls=utils.ws_futures_balance_data(balances, positions, self.wallet_state)
        )
