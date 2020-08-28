from typing import Optional
from mst_gateway.connector.api import OrderState
from .base import BitmexSerializer
from ...utils import load_order_side, load_order_type


class BitmexExecutionSerializer(BitmexSerializer):
    subscription = "execution"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        state_data = self._wss_api.storage.get(
            'symbol', self._wss_api.name, self._wss_api.schema
        ).get(item['symbol'].lower())
        if not state_data:
            return None
        data = dict(
            order_id=item.get('clOrdID'),
            symbol=item.get('symbol'),
            side=load_order_side(item.get('side')),
            tick_volume=item.get('lastQty'),
            tick_price=item.get('lastPx'),
            volume=item.get('orderQty'),
            price=item.get('price'),
            type=load_order_type(item.get('ordType')),
            status=self._order_status(item.get('ordStatus')),
            is_active=item.get('workingIndicator'),
            leaves_volume=item.get('leavesQty'),
            filled_volume=item.get('cumQty'),
            avg_price=item.get('avgPx'),
            timestamp=item.get('timestamp'),
            schema=state_data.get('schema'),
            system_symbol=state_data.get('system_symbol'),
        )
        return data

    def _order_status(self, status):
        if status.lower() == 'new':
            return OrderState.pending
        if status.lower() == 'partiallyfilled':
            return OrderState.active
        if status.lower() == 'filled':
            return OrderState.closed
