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
        if state := self._get_state(item.get('currency', '').lower()):
            balance = state[0]
            self._check_balances_data(balance, item)
        return load_wallet_data(item, is_for_ws=True)

    def _key_map(self, key: str):
        _map = {
            'bl': 'walletBalance',
            'mbl': 'marginBalance',
            'am': 'availableMargin',
            'im': 'initMargin',
            'wbl': 'withdrawableMargin',
            'mm': 'maintMargin',
            'upnl': 'unrealisedPnl'
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
        self._update_state(item.get('currency', '').lower(), valid_item)
        self._update_data(data, valid_item)
