from __future__ import annotations
from typing import Optional
from .base import BitmexSerializer
from ...utils import load_wallet_data


class BitmexWalletSerializer(BitmexSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == "margin"

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state = self._get_state('wallet')
        balances = state[0].get('balances', []) if state else []
        for balance in balances:
            if balance.get('currency', '').lower() == item.get('currency', '').lower():
                self._check_balances_data(balance, item)
        try:
            currencies = {}
            if self._wss_api.register_state:
                if (currencies := await self._wss_api.storage.get(
                        'currency', self._wss_api.name, self._wss_api.schema)) is None:
                    return None
            assets = ('btc', 'usd')
            fields = ('balance', 'unrealised_pnl', 'margin_balance')
            return load_wallet_data(item, currencies, assets, fields)
        except ConnectionError:
            return None

    def _key_map(self, key: str):
        _map = {
            'balance': 'walletBalance',
            'margin_balance': 'marginBalance',
            'available_margin': 'availableMargin',
            'init_margin': 'initMargin',
            'withdraw_balance': 'withdrawableMargin',
        }
        return _map.get(key)

    def _check_balances_data(self, balance, item):
        for k, v in balance.items():
            _mapped_key = self._key_map(k)
            if _mapped_key:
                item[_mapped_key] = balance[k]

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_state('wallet', valid_item)
        self._update_data(data, valid_item)
