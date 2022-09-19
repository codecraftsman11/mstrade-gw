from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from mst_gateway.connector.api.types import OrderSchema
from .base import BinanceSerializer
from ... import utils

if TYPE_CHECKING:
    from ... import BinanceWssApi


class BinanceWalletSerializer(BinanceSerializer):
    subscription = "wallet"
    table = 'outboundAccountPosition'

    def __init__(self, wss_api: BinanceWssApi):
        super().__init__(wss_api)
        self.state_data = wss_api.partial_state_data.get(self.subscription, {}).get(f"{self.subscription}_state", {})

    @property
    def _initialized(self) -> bool:
        return bool(self.subscription in self._wss_api.subscriptions)

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return bool(self._initialized and message['table'] == self.table)

    async def _load_data(self, message: dict, item: dict) -> Optional[list]:
        if not self.is_item_valid(message, item):
            return None
        return self._wallet_list(item)

    def _wallet_list(self, item: dict):
        if self._wss_api.schema == OrderSchema.exchange:
            return utils.ws_spot_wallet(item, self.state_data)
        return utils.ws_margin_cross_wallet(item, self.state_data)

    async def _append_item(self, data: list, message: dict, item: dict):
        valid_item = await self._load_data(message, item)
        if not valid_item:
            return None
        self._update_data(data, valid_item)


class BinanceWalletExtraSerializer(BinanceWalletSerializer):
    subscription = "wallet_extra"

    def _wallet_list(self, item: dict):
        return list(self.state_data.values())


class BinanceMarginWalletSerializer(BinanceWalletSerializer):
    table = 'ACCOUNT_UPDATE'

    def _wallet_list(self, item: dict):
        return utils.ws_futures_wallet(item, self.state_data)


class BinanceMarginWalletExtraSerializer(BinanceWalletExtraSerializer):
    table = 'ACCOUNT_UPDATE'

