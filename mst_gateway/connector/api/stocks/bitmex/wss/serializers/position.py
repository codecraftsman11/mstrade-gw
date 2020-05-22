from .base import BitmexSerializer


class BitmexPositionSerializer(BitmexSerializer):
    subscription = "position"

    def is_item_valid(self, message: dict, item: dict) -> bool:
        return True

    def _load_data(self, message: dict, item: dict) -> dict:
        data = dict(
                symbol=item.get('symbol'),
                mark_price=item.get('markPrice'),
                last_price=item.get('lastPrice'),
                volume=item.get('currentQty'),
                status=None,
                order_id=None,
                liquidation_price=item.get('liquidationPrice', None)
            )
        return data
