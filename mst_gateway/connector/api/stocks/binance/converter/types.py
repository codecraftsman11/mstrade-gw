from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema
)


class BinanceOrderTypeConverter(BaseOrderTypeConverter):
    """
    Order type converter for Binance

    """

    LOAD_TYPE_MAP = {
        OrderSchema.margin_cross: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with LONG type value
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin_isolated: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with LONG type value
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.exchange: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with number type value
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP': OrderType.stop_limit,
            'STOP_MARKET': OrderType.stop_market,
            'TAKE_PROFIT': OrderType.take_profit_limit,
            'TAKE_PROFIT_MARKET': OrderType.take_profit_market,
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin_coin: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP': OrderType.stop_limit,
            'STOP_MARKET': OrderType.stop_market,
            'TAKE_PROFIT': OrderType.take_profit_limit,
            'TAKE_PROFIT_MARKET': OrderType.take_profit_market,
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin_cross: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET',
        },
        OrderSchema.margin_isolated: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        },
        OrderSchema.exchange: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT_LIMIT',
            OrderType.take_profit_market: 'TAKE_PROFIT',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET',
        },
        OrderSchema.margin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        },
        OrderSchema.margin_coin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        }
    }

    @classmethod
    def prefetch_request_data(cls, schema: str, params: dict) -> dict:
        if schema in [OrderSchema.margin, OrderSchema.margin_coin]:
            if params['order_type'] in ['TRAILING_STOP_MARKET']:
                params['activationPrice'] = params['stop_price']
        return params

    @classmethod
    def prefetch_response_data(cls, schema: str, raw_data: dict) -> dict:
        if schema in [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated]:
            if raw_data['type'].upper() == 'STOP_LOSS' and raw_data.get('trailingDelta'):
                raw_data['type'] = 'TRAILING_STOP_MARKET'
        return raw_data
