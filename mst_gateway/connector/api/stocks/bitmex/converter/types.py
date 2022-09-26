from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """
    Order type converter for Bitmex

    custom args:
        ordType: TrailingStop
    """

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
            OrderType.take_profit_limit: 'LimitIfTouched',
            OrderType.take_profit_market: 'MarketIfTouched',
            OrderType.trailing_stop: 'TrailingStop'
        }
    }

    @classmethod
    def prefetch_request_data(cls, schema: str, params: dict) -> dict:
        # TODO: remove mock, calc real pegOffsetValue
        if params.get('order_type') == 'TrailingStop':
            params['pegOffsetValue'] = 100
            if params['side'] == 'Sell':
                params['pegOffsetValue'] *= -100
        return params

    @classmethod
    def prefetch_response_data(cls, schema: str, raw_data: dict) -> dict:
        if raw_data.get('pegPriceType') == 'TrailingStopPeg':
            raw_data['ordType'] = 'TrailingStop'
        return raw_data

    @classmethod
    def prefetch_message_data(cls, schema: str, item: dict) -> dict:
        if item.get('pegPriceType') == 'TrailingStopPeg':
            item['ordType'] = 'TrailingStop'
        return item
