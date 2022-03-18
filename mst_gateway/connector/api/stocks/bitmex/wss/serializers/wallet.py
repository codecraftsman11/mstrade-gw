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
        _cur = item.get('currency', '').lower()
        state = self._get_state(_cur)
        balances = state[0].get('bls', []) if state else []
        for balance in balances:
            if balance.get('cur', '').lower() == _cur:
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

    async def data(self, message) -> Optional[dict]:
        (action, data) = await self._get_data(message)
        if not data:
            return None
        data = data[0]
        return {
            'acc': self._wss_api.account_name,
            'tb': self.subscription,
            'sch': self._wss_api.schema,
            'act': action,
            'ex': data.pop('ex', None),
            'd': data,
        }
