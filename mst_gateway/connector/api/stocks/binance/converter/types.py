from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
    OrderExec
)


class BinanceOrderTypeConverter(BaseOrderTypeConverter):
    """ Order type converter for Binance """

    LOAD_TYPE_AND_EXECUTION_MAP = {
        OrderSchema.margin2: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.margin3: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.exchange: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP_LOSS_LIMIT': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT_LIMIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_LOSS': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'LIMIT_MAKER': {'type': OrderType.limit, 'execution': OrderExec.limit}
        },
        OrderSchema.futures: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_MARKET': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        },
        OrderSchema.futures_coin: {
            'LIMIT': {'type': OrderType.limit, 'execution': OrderExec.limit},
            'MARKET': {'type': OrderType.market, 'execution': OrderExec.market},
            'STOP': {'type': OrderType.stop_loss, 'execution': OrderExec.limit},
            'TAKE_PROFIT': {'type': OrderType.take_profit, 'execution': OrderExec.limit},
            # 'STOP_MARKET': {'type': OrderType.stop_loss, 'execution': OrderExec.market},
            # 'TAKE_PROFIT_MARKET': {'type': OrderType.take_profit, 'execution': OrderExec.market},
            # 'TRAILING_STOP_MARKET': {'type': OrderType.trailing_stop, 'execution': OrderExec.market},
        }
    }

    STORE_TYPE_MAP = {
        OrderType.limit: 'LIMIT',
        OrderType.market: 'MARKET',
        OrderType.position: 'MARKET',
    }
