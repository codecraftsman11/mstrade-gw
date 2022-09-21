from typing import Optional
from .order import OrderType


class BaseOrderTypeConverter:

    # Mapping must be defined in specific converters
    LOAD_TYPE_MAP = {}
    STORE_TYPE_BY_SCHEMA_MAP = {}

    @classmethod
    def load_order_type(cls, schema: str, exchange_order_type: str) -> Optional[str]:
        """
        Returns MST 'type' values based on exchange order type.

        """
        mapping_data = cls.LOAD_TYPE_MAP.get(schema, {})
        if order_type := mapping_data.get(exchange_order_type):
            return order_type
        return None

    @classmethod
    def store_type(cls, schema: str, order_type: str) -> str:
        """
        Returns exchange order type based on MST order type
        (market and limit only).

        """
        mapping_data = cls.STORE_TYPE_BY_SCHEMA_MAP.get(schema, {})
        if exchange_order_type := mapping_data.get(order_type):
            return exchange_order_type
        return OrderType.limit

    @classmethod
    def prefetch_request_data(cls, schema: str, params: dict) -> dict:
        return params

    @classmethod
    def prefetch_response_data(cls, schema: str, raw_data: dict) -> dict:
        return raw_data

    @classmethod
    def prefetch_message_data(cls, schema: str, item: dict) -> dict:
        return item
