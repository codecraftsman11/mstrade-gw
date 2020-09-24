from __future__ import annotations
from typing import Optional
from mst_gateway.connector.api.types import OrderSchema
from .base import BinanceSerializer
from ... import utils


class BinanceWalletSerializer(BinanceSerializer):
    subscription = "wallet"

    def is_item_valid(self, message: dict, item) -> bool:
        return message.get('e') == 'outboundAccountPosition'

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        state_data = self._wss_api.storage.get(
            f'{self.subscription}.{self._wss_api.account_name}', schema=self._wss_api.schema
        )
        if not state_data:
            return
        if isinstance(self._wss_api.subscriptions.get(self.subscription), dict):
            return self._wallet_detail(item, state_data)
        else:
            currencies = self._wss_api.storage.get('currency', self._wss_api.name, self._wss_api.schema)
            if not currencies:
                return
            return self._wallet_list(item, state_data, currencies)

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        if self._wss_api.schema == OrderSchema.exchange:
            fields = ('balance',)
            return utils.ws_spot_wallet(item, state_data, currencies, assets, fields)
        elif self._wss_api.schema == OrderSchema.margin2:
            fields = ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed')
            return utils.ws_margin_wallet(item, state_data, currencies, assets, fields)

    def _wallet_detail(self, item, state_data):
        _state_balances = state_data.pop('balances', dict())
        if self._wss_api.schema == OrderSchema.exchange:
            return dict(balances=utils.ws_spot_balance_data(item.get('B'), _state_balances))
        elif self._wss_api.schema == OrderSchema.margin2:
            return dict(balances=utils.ws_margin_balance_data(item.get('B'), _state_balances))

    def _append_item(self, data: list, message: dict, item: dict):
        valid_item = self._load_data(message, item)
        self._update_data(data, valid_item)


class BinanceFuturesWalletSerializer(BinanceWalletSerializer):

    def is_item_valid(self, message: dict, item) -> bool:
        return message.get('e') == 'ACCOUNT_UPDATE'

    def _wallet_list(self, item, state_data: dict, currencies: dict):
        assets = ('btc', 'usd')
        fields = ('balance', 'unrealised_pnl', 'margin_balance')
        return utils.ws_futures_wallet(item, state_data, currencies, assets, fields)

    def _wallet_detail(self, item, state_data):
        balances = item['a']['B']
        _state_balances = state_data.pop('balances', dict())
        return dict(
            balances=utils.ws_futures_balance_data(balances, item['a'].get('P', list()), _state_balances)
        )
