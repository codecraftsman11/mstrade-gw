from .order import OrderType


class BaseOrderTypeConverter:

    # Mapping must be defined in specific converters
    LOAD_TYPE_AND_EXECUTION_MAP = dict()
    STORE_TYPE_BY_SCHEMA_MAP = dict()

    @classmethod
    def load_type_and_exec(cls, schema: str, exchange_order_type: str) -> dict:
        """
        Returns MST 'type' and 'execution' values based on
        exchange order type.

        """
        mapping_data = cls.LOAD_TYPE_AND_EXECUTION_MAP.get(schema, dict())
        if order_type_and_exec := mapping_data.get(exchange_order_type):
            return order_type_and_exec
        return {'type': None, 'execution': None}

    @classmethod
    def store_type(cls, order_type: str, schema: str) -> str:
        """
        Returns exchange order type based on MST order type
        (market and limit only).

        """
        mapping_data = cls.STORE_TYPE_BY_SCHEMA_MAP.get(schema, dict())
        if exchange_order_type := mapping_data.get(order_type):
            return exchange_order_type
        return OrderType.limit
