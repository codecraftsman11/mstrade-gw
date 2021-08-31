from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .base import BitmexSerializer
from ...utils import load_wallet_data

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexWalletSerializer(BitmexSerializer):
    subscription = "wallet"

    def __init__(self, wss_api: BitmexWssApi):
        super().__init__(wss_api)
        self._state_data = wss_api.partial_state_data[self.subscription]

    @property
    def exchange_rates(self):
        return self._state_data.get('exchange_rates', {})

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == "margin"

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state = self._get_state('wallet')
        balances = state[0].get('bls', []) if state else []
        for balance in balances:
            if balance.get('cur', '').lower() == item.get('currency', '').lower():
                self._check_balances_data(balance, item)
        if self._wss_api.register_state and not self.exchange_rates:
            return None
        assets = ('btc', 'usd')
        fields = ('bl', 'upnl', 'mbl')
        return load_wallet_data(item, self.exchange_rates, assets, fields, is_for_ws=True)

    def _key_map(self, key: str):
        _map = {
            'bl': 'walletBalance',
            'mbl': 'marginBalance',
            'am': 'availableMargin',
            'im': 'initMargin',
            'wbl': 'withdrawableMargin',
        }
        return _map.get(key)

    def _check_balances_data(self, balance, item):
        for k, v in balance.items():
            _mapped_key = self._key_map(k)
            if _mapped_key not in item:
                item[_mapped_key] = balance[k]

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_state('wallet', valid_item)
        self._update_data(data, valid_item)
