from .order import OrderSchema
from .serializers import (
    Margin1OrderTypeSerializer,
    Margin2OrderTypeSerializer,
    ExchangeOrderTypeSerializer,
    FuturesOrderTypeSerializer
)


class OrderTypeFactory:
    serializers = {
        OrderSchema.margin1: Margin1OrderTypeSerializer,
        OrderSchema.margin2: Margin2OrderTypeSerializer,
        OrderSchema.exchange: ExchangeOrderTypeSerializer,
        OrderSchema.futures: FuturesOrderTypeSerializer
    }

    def get_serializer(self, schema):
        serializer = self.serializers.get(schema)
        if not serializer:
            raise ValueError(schema)
        return serializer()


class SchemaOrderType:
    factory = OrderTypeFactory()

    def __init__(self, schema):
        self.serializer = self.factory.get_serializer(schema)

    def load_order_type(self, exchange_order_type):
        return self.serializer.load_order_type(exchange_order_type)

    def store_order_type(self, order_type, order_execution):
        return self.serializer.store_order_type(order_type, order_execution)
