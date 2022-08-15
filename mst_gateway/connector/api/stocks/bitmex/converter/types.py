from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
    OrderExec,
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Bitmex """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin: {
            'Market': {'type': OrderType.market, 'execution': OrderExec.market},
            'Limit': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'Stop': {'type': OrderType.stop_market, 'execution': OrderExec.market},
            'StopLimit': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            # 'MarketIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LimitIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin: {
            OrderType.limit: 'Limit',
            OrderType.market: 'Market',
            OrderType.stop_market: 'Stop',
            OrderType.stop_limit: 'StopLimit'
        }
    }
