import abc
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
    def store_type(cls, schema: str, order_type: Optional[str]) -> str:
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

    @classmethod
    def generate_parameters_by_order_type(cls, main_params: dict, options: dict, schema: str) -> dict:
        """
        Fetches specific order parameters based on the order_type value and adds them
        to the main parameters.

        """
        order_type = main_params.pop('order_type', None)
        exchange_order_type = cls.store_type(schema, order_type)
        prefetched_parameters = cls.prefetch_request_data(schema,
                                                          {'order_type': exchange_order_type, **main_params, **options})
        mapping_parameters = cls._store_order_mapping_parameters(exchange_order_type, schema)
        params = cls._assign_custom_parameter_values(schema, prefetched_parameters)
        all_params = cls.map_api_parameter_names(
            schema,
            {'order_type': exchange_order_type, **params}
        )
        new_params = {}
        for param_name in mapping_parameters:
            value = all_params.get(param_name)
            if value:
                new_params[param_name] = value
        new_params.update(
            cls._store_order_additional_parameters(exchange_order_type, schema)
        )
        return new_params

    @classmethod
    @abc.abstractmethod
    def _store_order_mapping_parameters(cls, exchange_order_type: str, schema: str) -> list:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def _assign_custom_parameter_values(cls, schema: str, options: Optional[dict]) -> dict:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def map_api_parameter_names(cls, schema: str, params: dict) -> Optional[dict]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def _store_order_additional_parameters(cls, exchange_order_type: str, schema: str) -> dict:
        raise NotImplementedError
