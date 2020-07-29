from __future__ import annotations
from .base import BinanceSerializer
from ... import utils


class BinanceWalletSerializer(BinanceSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item) -> bool:
        return message.get('e') in ('outboundAccountInfo', 'ACCOUNT_UPDATE')

    def _load_data(self, message: dict, item: dict) -> dict:
        if self._wss_api.schema == 'exchange':
            return utils.ws_spot_wallet(item=item)
        elif self._wss_api.schema == 'margin2':
            return utils.ws_margin_wallet(item=item)
        elif self._wss_api.schema == 'futures':
            return utils.ws_futures_wallet(item=item)

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_data(data, valid_item)
