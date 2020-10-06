# in serializers.py
import json
from abc import abstractmethod
from mst_gateway.connector import api


class SerializerFactory:
    def __init__(self):
        self._creators = {
            api.OrderSchema.margin1: Margin1Serializer
        }

    def get_serializer(self, schema):
        serializer = self._creators.get(schema)
        if not serializer:
            raise ValueError(schema)
        return serializer()


class OrderType:
    def __init__(self, order_type, order_execution, schema):
        self.factory = SerializerFactory()
        self.type = order_type
        self.execution = order_execution
        self.schema = schema

    def serialize(self):
        serializer = self.factory.get_serializer(self.schema)
        return serializer.store_order_type(self.type, self.execution)


class BaseSerializer:
    LOAD_TYPE_AND_EXECUTION_MAP = dict()
    STORE_TYPE_AND_EXECUTION_MAP = dict()

    # @abstractmethod
    def store_order_type(self, type, execution):
        order_type = self.STORE_TYPE_AND_EXECUTION_MAP.get(f'{type}|{execution}'.lower())
        if order_type:
            return order_type
        return self.STORE_TYPE_AND_EXECUTION_MAP[f'{api.OrderType.limit}|{api.OrderExec.limit}']

    def load_order_type(self, exchange_type):
        order_type = self.LOAD_TYPE_AND_EXECUTION_MAP.get(exchange_type)
        return order_type if order_type else None


class Margin1Serializer(BaseSerializer):
    def __init__(self):
        self.LOAD_TYPE_AND_EXECUTION_MAP = {
            'Market': {'type': api.OrderType.market, 'execution': api.OrderExec.market},
            'Limit': {'type': api.OrderType.limit, 'execution': api.OrderExec.limit},
            'Stop': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.market},
            'StopLimit': {'type': api.OrderType.stop_loss, 'execution': api.OrderExec.limit},
            'MarketIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.market},
            'LimitIfTouched': {'type': api.OrderType.take_profit, 'execution': api.OrderExec.limit},
        }
        self.STORE_TYPE_AND_EXECUTION_MAP = {
            f'{api.OrderType.market}|{api.OrderExec.market}': 'Market',
            f'{api.OrderType.limit}|{api.OrderExec.limit}': 'Limit',
            f'{api.OrderType.stop_loss}|{api.OrderExec.market}': 'Stop',
            f'{api.OrderType.stop_loss}|{api.OrderExec.limit}': 'StopLimit',
            f'{api.OrderType.take_profit}|{api.OrderExec.market}': 'MarketIfTouched',
            f'{api.OrderType.take_profit}|{api.OrderExec.limit}': 'LimitIfTouched',
            # We currently map TS-MARKET to 'Stop', but it can also work with 'MarketIfTouched'
            f'{api.OrderType.trailing_stop}|{api.OrderExec.market}': 'Stop',
            # We currently map TS-LIMIT to 'StopLimit', but it can also work with 'LimitIfTouched':
            f'{api.OrderType.trailing_stop}|{api.OrderExec.limit}': 'StopLimit'
        }


order = OrderType('limit', 'limit', api.OrderSchema.margin1)
print(order.serialize())
