from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Bitmex """

    LOAD_TYPE_MAP = {
        OrderSchema.margin: {
            'Market': OrderType.market,
            'Limit': OrderType.limit,
            'Stop': OrderType.stop_market,
            'StopLimit': OrderType.stop_limit,
            'MarketIfTouched': OrderType.take_profit_market,
            'LimitIfTouched': OrderType.take_profit_limit,
            # use TrailingStop if exchange order data contain a pegPriceType field with value "TrailingStopPeg"
            'TrailingStop': OrderType.trailing_stop,
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin: {
            OrderType.limit: 'Limit',
            OrderType.market: 'Market',
            OrderType.stop_market: 'Stop',
            OrderType.stop_limit: 'StopLimit',
            OrderType.trailing_stop: 'Stop',
            OrderType.take_profit_limit: 'LimitIfTouched',
            OrderType.take_profit_market: 'MarketIfTouched'
        }
    }
