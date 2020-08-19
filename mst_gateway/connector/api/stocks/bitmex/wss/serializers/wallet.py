from __future__ import annotations
from typing import Optional
from .base import BitmexSerializer
from ...utils import load_wallet_data, load_wallet_detail_data


class BitmexWalletSerializer(BitmexSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == "margin"

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        state = self._get_state('wallet')
        balances = state[0].get('balances') if state else list()
        for balance in balances:
            self._check_balances_data(balance, item)
        return load_wallet_data(item)

    def _check_balances_data(self, balance, item):
        if balance.get('currency', '').lower() == item.get('currency').lower():
            if not item.get('walletBalance'):
                item['walletBalance'] = balance['balance']
            if not item.get('marginBalance'):
                item['marginBalance'] = balance['margin_balance']
            if not item.get('availableMargin'):
                item['availableMargin'] = balance['available_margin']
            if not item.get('initMargin'):
                item['initMargin'] = balance['init_margin']
            if not item.get('withdrawableMargin'):
                item['withdrawableMargin'] = balance['withdraw_balance']
            return item

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_state('wallet', valid_item)
        self._update_data(data, valid_item)
