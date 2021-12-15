from mst_gateway.connector.api import BUY, SELL, OrderSchema, OrderExec, OrderType

DEFAULT_SYMBOL = "XBTUSD"
DEFAULT_SYSTEM_SYMBOL = "btcusd"
DEFAULT_SCHEMA = OrderSchema.margin1
DEFAULT_ORDER_TYPE = OrderType.limit
DEFAULT_ORDER_SIDE = BUY
DEFAULT_ORDER_OPPOSITE_SIDE = SELL
DEFAULT_ORDER_VOLUME = {
    OrderSchema.margin1: 100
}
DEFAULT_ORDER_OPTIONS = {}
DEFAULT_ORDER = {
    OrderSchema.margin1: {
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.margin1,
        'side': DEFAULT_ORDER_SIDE,
        'stop': None,
        'symbol': DEFAULT_SYMBOL,
        'system_symbol': DEFAULT_SYSTEM_SYMBOL,
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.margin1],
    }
}