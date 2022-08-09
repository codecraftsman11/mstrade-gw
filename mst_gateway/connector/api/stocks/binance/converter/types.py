from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
    OrderExec
)


class BinanceOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Binance """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin_cross: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.margin_isolated: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.exchange: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.margin: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            'STOP_MARKET': {'type': OrderType.stop_market, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        },
        OrderSchema.margin_coin: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_limit, 'execution': OrderExec.limit},
            'STOP_MARKET': {'type': OrderType.stop_market, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin_cross: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET'
        },
        OrderSchema.margin_isolated: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
        },
        OrderSchema.exchange: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET'
        },
        OrderSchema.margin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET'
        },
        OrderSchema.margin_coin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET'
        }
    }
