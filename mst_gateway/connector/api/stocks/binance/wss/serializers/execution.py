from __future__ import annotations
from typing import Optional
from .base import BinanceSerializer
from ...... import api
from ... import utils
from ... import var


class BinanceExecutionSerializer(BinanceSerializer):
    subscription = "execution"

    def is_item_valid(self, message: dict, item) -> bool:
        raw_data = message.get('o') if self._wss_api.schema == api.OrderSchema.futures else message
        return message.get('e') in (
            'executionReport', 'ORDER_TRADE_UPDATE'
        ) and raw_data.get('X') in var.BINANCE_EXECUTION_STATUS_MAP.keys()

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        raw_data = item.get('o') if self._wss_api.schema == api.OrderSchema.futures else item

        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(
            raw_data['s'].lower()
        ) if raw_data and raw_data.get('s') else None
        if not state_data:
            return None

        return utils.load_execution_ws_data(
            message_data=item,
            raw_data=raw_data,
            state_data=state_data,
        )
