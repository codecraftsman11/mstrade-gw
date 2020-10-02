from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...... import api
from ... import utils
from ... import var


class BinanceOrderSerializer(BinanceSerializer):
    subscription = "order"

    def is_item_valid(self, message: dict, item) -> bool:
        raw_data = message.get('o') if self._wss_api.schema == api.OrderSchema.futures else message
        return message.get('e') in (
            'executionReport', 'ORDER_TRADE_UPDATE'
        ) and raw_data.get('o') in var.BINANCE_ORDER_TYPE_AND_EXECUTION_MAP.keys()

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if self._wss_api.schema == api.OrderSchema.futures:
            item.update(item.get('o'))
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(
            item['s'].lower()
        ) if item and item.get('s') else None
        if not state_data:
            return None
        return utils.load_order_ws_data(
            raw_data=item,
            state_data=state_data,
        )
