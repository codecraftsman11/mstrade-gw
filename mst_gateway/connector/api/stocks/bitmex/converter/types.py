from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
    OrderExec
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Bitmex """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin: {
            'Market': {'type': OrderType.market, 'execution': OrderExec.market},
            'Limit': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'StopLimit': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'LimitIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'Stop': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'MarketIfTouched': {'type': OrderType.take_profit, 'execution': OrderExec.market},
        }
    }

    STORE_TYPE_MAP = {
        OrderType.limit: 'Limit',
        OrderType.market: 'Market',
        OrderType.position: 'Market',
    }
