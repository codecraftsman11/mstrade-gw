from __future__ import annotations
from .base import BinanceSerializer
from ... import utils


class BinanceWalletSerializer(BinanceSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item) -> bool:
        if isinstance(self._wss_api.subscriptions.get('wallet'), dict):
            return message.get('e') == 'outboundAccountPosition'
        return message.get('e') == 'outboundAccountInfo'

    def _load_data(self, message: dict, item: dict) -> dict:
        if message.get('table') == 'outboundAccountPosition':
            return self._wallet_detail(item)
        else:
            return self._wallet_list(item)

    def _wallet_list(self, item):
        if self._wss_api.schema == 'exchange':
            return utils.ws_spot_wallet(item=item)
        elif self._wss_api.schema == 'margin2':
            return utils.ws_margin_wallet(item=item)

    def _wallet_detail(self, item):
        if self._wss_api.schema == 'exchange':
            return dict(balances=utils.ws_spot_balance_data(item.get('B')))
        elif self._wss_api.schema == 'margin2':
            return dict(balances=utils.ws_margin_balance_data(item.get('B')))

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_data(data, valid_item)


class BinanceFuturesWalletSerializer(BinanceWalletSerializer):

    def is_item_valid(self, message: dict, item) -> bool:
        return message.get('e') == 'ACCOUNT_UPDATE'

    def _load_data(self, message: dict, item: dict) -> dict:
        if isinstance(self._wss_api.subscriptions.get('wallet'), dict):
            return self._wallet_detail(item)
        else:
            return self._wallet_list(item)

    def _wallet_list(self, item):
        return utils.ws_futures_wallet(item=item)

    def _wallet_detail(self, item):
        balances = item['a']['B']
        return dict(
            balances=utils.ws_futures_balance_data(balances, item.get('a', dict()).get('P', list()))
        )
