from typing import Optional
from .base import BitmexSerializer
from ... import utils
from mst_gateway.connector.api.types.order import LeverageType


class BitmexPositionSerializer(BitmexSerializer):
    subscription = "position"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    async def _load_data(self, message: dict, item: dict) -> Optional[dict]:
        if not self.is_item_valid(message, item):
            return None
        state_data = None
        if self._wss_api.register_state:
            if (state_data := self._wss_api.get_state_data(item.get('symbol'))) is None:
                return None
        state = self._get_state(item.get('symbol'))
        if state:
            if item.get('avgEntryPrice') is None:
                item['avgEntryPrice'] = state[0]['entry_price']
            if item.get('liquidationPrice') is None:
                item['liquidationPrice'] = state[0]['liquidation_price']
            if item.get('unrealisedPnl') is None:
                item['unrealisedPnl'] = state[0]['unrealised_pnl']
            if item.get('leverage') is None:
                item['leverage'] = state[0]['leverage']
            if item.get('crossMargin') is None:
                item['crossMargin'] = state[0]['leverage_type'] == LeverageType.cross
            if item.get('markPrice') is None:
                item['markPrice'] = state[0]['mark_price']
        return utils.load_position_ws_data(item, state_data)
