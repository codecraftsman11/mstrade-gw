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

    def get_serializer(self, schema: str):
        serializer = self.serializers.get(schema)
        if not serializer:
            raise ValueError(schema)
        return serializer()


class OrderTypeConverter:
    """
    Converts MST order type to Schema order type and vice versa.

    """
    factory = OrderTypeFactory()

    def __init__(self, schema: str):
        self.serializer = self.factory.get_serializer(schema)

    def load_order_type(self, exchange_order_type: str) -> dict:
        return self.serializer.load_order_type(exchange_order_type)

    def store_order_type(self, order_type: str, order_execution: str) -> str:
        return self.serializer.store_order_type(order_type, order_execution)
