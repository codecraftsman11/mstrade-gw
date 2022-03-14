from __future__ import annotations
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

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item) or not self.wallet_state:
            return None
        return self._wallet_list(item)

    def _wallet_list(self, item):
        if self._wss_api.schema == OrderSchema.exchange:
            return utils.ws_spot_wallet(item, self.wallet_state)
        elif self._wss_api.schema == OrderSchema.margin_cross:
            return utils.ws_margin_cross_wallet(item, self.wallet_state)

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
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


class BinanceMarginWalletSerializer(BinanceWalletSerializer):

    def is_item_valid(self, message: dict, item) -> bool:
        return message['table'] == 'ACCOUNT_UPDATE' and self.subscription in self._wss_api.subscriptions

    def _wallet_list(self, item):
        if self._wss_api.schema == OrderSchema.margin_coin:
            return utils.ws_margin_coin_wallet(item, self.wallet_state)
        else:
            return utils.ws_margin_wallet(item, self.wallet_state)
