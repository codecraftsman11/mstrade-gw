from .order import OrderType, OrderExec


class OrderTypeSerializer:
    LOAD_TYPE_AND_EXECUTION_MAP = dict()
    STORE_TYPE_AND_EXECUTION_MAP = dict()

    def load_order_type(self, exchange_order_type):
        order_type = self.LOAD_TYPE_AND_EXECUTION_MAP.get(exchange_order_type)
        if not order_type:
            raise ValueError(exchange_order_type)
        return order_type

    def store_order_type(self, order_type, order_execution):
        order_type = self.STORE_TYPE_AND_EXECUTION_MAP.get(f'{order_type}|{order_execution}'.lower())
        if order_type:
            return order_type
        return self.STORE_TYPE_AND_EXECUTION_MAP[f'{OrderType.limit}|{OrderExec.limit}']


class Margin1OrderTypeSerializer(OrderTypeSerializer):
    def __init__(self):
        self.LOAD_TYPE_AND_EXECUTION_MAP = {
            'Market': {'type': OrderType.market, 'execution': OrderExec.market},
            'Limit': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'Stop': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'StopLimit': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'MarketIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'LimitIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
        }
        self.STORE_TYPE_AND_EXECUTION_MAP = {
            f'{OrderType.market}|{OrderExec.market}': 'Market',
            f'{OrderType.limit}|{OrderExec.limit}': 'Limit',
            f'{OrderType.stop_loss}|{OrderExec.market}': 'Market',
            f'{OrderType.stop_loss}|{OrderExec.limit}': 'Limit',
            f'{OrderType.take_profit}|{OrderExec.market}': 'Market',
            f'{OrderType.take_profit}|{OrderExec.limit}': 'Limit',
            f'{OrderType.trailing_stop}|{OrderExec.market}': 'Market',
            f'{OrderType.trailing_stop}|{OrderExec.limit}': 'Limit'
        }


class Margin2OrderTypeSerializer(OrderTypeSerializer):
    def __init__(self):
        self.LOAD_TYPE_AND_EXECUTION_MAP = {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        }
        self.STORE_TYPE_AND_EXECUTION_MAP = {
            f'{OrderType.limit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.market}|{OrderExec.market}': 'MARKET',
            f'{OrderType.stop_loss}|{OrderExec.market}': 'MARKET',
            f'{OrderType.stop_loss}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.take_profit}|{OrderExec.market}': 'MARKET',
            f'{OrderType.take_profit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.limit}|{OrderExec.market}': 'MARKET',
        }


class ExchangeOrderTypeSerializer(OrderTypeSerializer):
    def __init__(self):
        self.LOAD_TYPE_AND_EXECUTION_MAP = {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        }
        self.STORE_TYPE_AND_EXECUTION_MAP = {
            f'{OrderType.limit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.market}|{OrderExec.market}': 'MARKET',
            f'{OrderType.stop_loss}|{OrderExec.market}': 'MARKET',
            f'{OrderType.stop_loss}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.take_profit}|{OrderExec.market}': 'MARKET',
            f'{OrderType.take_profit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.limit}|{OrderExec.market}': 'MARKET',
        }


class FuturesOrderTypeSerializer(OrderTypeSerializer):
    def __init__(self):
        self.LOAD_TYPE_AND_EXECUTION_MAP = {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'STOP_MARKET': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        }
        self.STORE_TYPE_AND_EXECUTION_MAP = {
            f'{OrderType.limit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.market}|{OrderExec.market}': 'MARKET',
            f'{OrderType.stop_loss}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.stop_loss}|{OrderExec.market}': 'MARKET',
            f'{OrderType.take_profit}|{OrderExec.limit}': 'LIMIT',
            f'{OrderType.take_profit}|{OrderExec.market}': 'MARKET',
            f'{OrderType.trailing_stop}|{OrderExec.market}': 'MARKET',
        }
