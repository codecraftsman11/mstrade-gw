from ....wss.serializer import Serializer


class BitmexSerializer(Serializer):
    subscription = "base"

    def is_valid(self):
        return True

    @classmethod
    def is_item_valid(cls, item: dict) -> bool:
        # pylint: disable=unused-argument
        return False


class BitmexSymbolSerializer(BitmexSerializer):
    subscription = "symbol"

    @classmethod
    def is_item_valid(cls, item: dict) -> bool:
        return 'lastPrice' in item


class BitmexQuoteBinSerializer(BitmexSerializer):
    subscription = "quote_bin"

    @classmethod
    def is_item_valid(cls, item: dict) -> bool:
        return 'price' in item


class BitmexOrderSerializer(BitmexSerializer):
    subscription = "order"

    @classmethod
    def is_item_valid(cls, item: dict) -> bool:
        return 'price' in item
