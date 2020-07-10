from __future__ import annotations
from .base import BitmexSerializer
from ...utils import load_wallet_data


class BitmexWalletSerializer(BitmexSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return message.get('table') == "margin"

    def _load_data(self, message: dict, item: dict) -> dict:
        state = self._get_state('wallet')
        balances = state[0]['balances'] if state else list()
        for balance in balances:
            if balance.get('currency').lower() == item.get('currency').lower():
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
        return load_wallet_data(item)

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_state('wallet', valid_item)
        self._update_data(data, valid_item)
