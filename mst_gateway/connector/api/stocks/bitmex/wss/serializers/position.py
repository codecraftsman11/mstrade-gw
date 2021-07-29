from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from .base import BitmexSerializer
from ... import utils
from mst_gateway.connector.api.types.order import LeverageType

if TYPE_CHECKING:
    from ... import BitmexWssApi


class BitmexPositionSerializer(BitmexSerializer):
    subscription = "position"

    def __init__(self, wss_api: BitmexWssApi):
        super().__init__(wss_api)
        self.exchange_rates = wss_api.partial_state_data.get(self.subscription, {}).get('exchange_rates', {})

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
            item['state_volume'] = state[0]['vl']
            if item.get('avgEntryPrice') is None:
                item['avgEntryPrice'] = state[0]['ep']
            if item.get('liquidationPrice') is None:
                item['liquidationPrice'] = state[0]['lp']
            if item.get('unrealisedPnl') is None:
                item['unrealisedPnl'] = state[0]['upnl']
            if item.get('leverage') is None:
                item['leverage'] = state[0]['lvr']
            if item.get('crossMargin') is None:
                item['crossMargin'] = state[0]['lvrp'] == LeverageType.cross
            if item.get('markPrice') is None:
                item['markPrice'] = state[0]['mp']
            if not item.get('currentQty'):
                item['side'] = state[0]['sd']
                item['currentQty'] = state[0]['vl']
        else:
            item['state_volume'] = item.get('currentQty')
        return utils.load_position_ws_data(item, state_data, self.exchange_rates)
