from .order import OrderType, OrderExec, OrderSchema


class BaseOrderTypeConverter:

    LOAD_TYPE_AND_EXECUTION_MAP = dict()

    STORE_TYPE_MAP = dict()

    # Universal mapping to convert any MST order into 'limit' or 'market'
    STORE_TYPE_AND_EXECUTION_MAP = {
        f'{OrderType.limit}|{OrderExec.limit}': OrderType.limit,
        f'{OrderType.limit}|{OrderExec.market}': OrderType.limit,
        f'{OrderType.market}|{OrderExec.market}': OrderType.market,
        f'{OrderType.market}|{OrderExec.limit}': OrderType.market,
        f'{OrderType.stop_loss}|{OrderExec.market}': OrderType.market,
        f'{OrderType.stop_loss}|{OrderExec.limit}': OrderType.limit,
        f'{OrderType.take_profit}|{OrderExec.market}': OrderType.market,
        f'{OrderType.take_profit}|{OrderExec.limit}': OrderType.limit,
        f'{OrderType.trailing_stop}|{OrderExec.market}': OrderType.market,
        f'{OrderType.trailing_stop}|{OrderExec.limit}': OrderType.limit,
    }

    @classmethod
    def store_type_and_exec(cls, order_type: str, order_execution: str) -> str:
        """
        Converts MST order type and execution to either
        'limit' or 'market'.

        """
        type_and_execution = f'{order_type}|{order_execution}'.lower()
        order_type = cls.STORE_TYPE_AND_EXECUTION_MAP.get(type_and_execution)
        if order_type:
            return order_type
        return OrderType.limit

    @classmethod
    def load_type_and_exec(cls, schema: str, exchange_order_type: str) -> dict:
        """
        Returns MST 'type' and 'execution' values based on
        exchange order type.

        """
        mapping_data = cls.LOAD_TYPE_AND_EXECUTION_MAP.get(schema, dict())
        order_type_and_exec = mapping_data.get(exchange_order_type)
        if order_type_and_exec:
            return order_type_and_exec
        return {'type': None, 'execution': None}

    @classmethod
    def store_type(cls, order_type: str) -> str:
        """
        Returns exchange order type based on MST order type
        (market and limit only).

        """
        exchange_order_type = cls.STORE_TYPE_MAP.get(order_type)
        if exchange_order_type:
            return exchange_order_type
        return OrderType.limit


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Bitmex """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin1: {
            'Market': {'type': OrderType.market, 'execution': OrderExec.market},
            'Limit': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'Stop': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'StopLimit': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'MarketIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'LimitIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
        }
    }

    STORE_TYPE_MAP = {
        OrderType.limit: 'Limit',
        OrderType.market: 'Market'
    }


class BinanceOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Binance """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin2: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.exchange: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.futures: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'STOP_MARKET': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        }
    }

    STORE_TYPE_MAP = {
        OrderType.limit: 'LIMIT',
        OrderType.market: 'MARKET',
    }
