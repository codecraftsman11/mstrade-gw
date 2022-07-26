from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
    OrderExec,
)
from mst_gateway.connector.api.stocks.bitmex.var import (
    BITMEX_BUY, BITMEX_SELL
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Bitmex """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin: {
            'Market': {'type': OrderType.market, 'execution': OrderExec.market},
            'Limit': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'Stop': {'type': OrderType.stop_market, 'execution': OrderExec.limit},
            'StopLimit': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            'MarketIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            'LimitIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
        }
    }
    BASE_STORE_TYPE_MAP = {
        OrderType.limit: 'Limit',
        OrderType.market: 'Market',
        OrderType.position: 'Market',
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin: {
            OrderType.stop_market: 'Stop',
            OrderType.stop_limit: 'StopLimit'
        }
    }
