from __future__ import annotations
from typing import Optional
from .base import BitmexSerializer
from ...utils import load_wallet_data, load_wallet_detail_data


class BitmexWalletSerializer(BitmexSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == "margin"

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state = self._get_state('wallet')
        balances = state[0].get('balances', []) if state else []
        for balance in balances:
            if balance.get('currency', '').lower() == item.get('currency', '').lower():
                self._check_balances_data(balance, item)
        try:
            return load_wallet_data(item)
        except ConnectionError:
            return None

    def _key_map(self, key: str):
        _map = {
            'walletBalance': 'balance',
            'marginBalance': 'margin_balance',
            'availableMargin': 'available_margin',
            'initMargin': 'init_margin',
            'withdrawableMargin': 'withdraw_balance',
        }
        return _map.get(key)

    def _check_balances_data(self, balance, item):
        for k, v in item.items():
            _mapped_key = self._key_map(k)
            if v is None and _mapped_key:
                item[k] = balance[_mapped_key]

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        if not valid_item:
            return None
        self._update_state('wallet', valid_item)
        self._update_data(data, valid_item)
