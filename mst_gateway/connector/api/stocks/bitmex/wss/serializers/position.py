from .base import BitmexSerializer


class BitmexPositionSerializer(BitmexSerializer):
    subscription = "position"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    def _load_data(self, message: dict, item: dict) -> dict:
        state = self._get_state(item.get('symbol'))
        if not item.get('avgEntryPrice'):
            item['avgEntryPrice'] = state[0]['entry_price']
        if not item.get('liquidationPrice'):
            item['liquidationPrice'] = state[0]['liquidation_price']

        data = dict(
                timestamp=item.get('timestamp'),
                symbol=item.get('symbol'),
                mark_price=item.get('markPrice'),
                last_price=item.get('lastPrice'),
                volume=item.get('currentQty'),
                liquidation_price=item.get('liquidationPrice'),
                entry_price=item.get('avgEntryPrice')
            )
        return data
