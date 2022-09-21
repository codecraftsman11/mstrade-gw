from mst_gateway.utils import ClassWithAttributes


class OrderType(ClassWithAttributes):
    market = 'market'
    limit = 'limit'
    stop_market = 'stop_market'
    stop_limit = 'stop_limit'
    take_profit_market = 'take_profit_market'
    take_profit_limit = 'take_profit_limit'
    trailing_stop = 'trailing_stop'


class OrderSchema(ClassWithAttributes):
    exchange = 'exchange'
    margin = 'margin'
    margin_cross = 'margin_cross'
    margin_isolated = 'margin_isolated'
    margin_coin = 'margin_coin'


class OrderSchemaTradeMode(ClassWithAttributes):
    exchange = ['trade', 'exchange']
    margin = ['margin']
    margin_cross = ['margin_cross']
    margin_isolated = ['margin_isolated']
    margin_coin = ['margin_coin']

    @classmethod
    def schema_pairs(cls):
        return tuple((i[0], i[0]) for i in cls._attributes())

    @classmethod
    def trade_mode_pairs(cls):
        _pairs = []
        for i in cls._attributes():
            _pairs.extend(i[1])
        return tuple((p, p) for p in _pairs)

    @classmethod
    def trade_mode(cls, schema):
        _d = {i[0]: i[1] for i in cls._attributes()}
        return _d.get(schema)

    @classmethod
    def position_trade_mode(cls, schema):
        _d = {i[0]: i[1][0] for i in cls._attributes()}
        return _d.get(schema)


class OrderState(ClassWithAttributes):
    waiting = 'waiting'         # Algorithm is waiting for start
    started = 'started'         # Algorithm is started
    canceled = 'canceled'       # Algorithm is canceled
    expired = 'expired'         # Limit order is expired
    pending = 'pending'         # Limit order is waiting to activate
    deleted = 'deleted'         # Limit order is deleted
    active = 'active'           # Position order is active
    closed = 'closed'           # Position order is closed
    reversed = 'reversed'       # Position order is reversed
    liquidated = 'liquidated'   # Position order is liquidated


class OrderTTL(ClassWithAttributes):
    GTC = 'GTC'
    IOC = 'IOC'
    FOK = 'FOK'


class OrderParams(ClassWithAttributes):
    iceberg = 'iceberg'
    passive = 'passive'
    post_only = 'post_only'
    reduce_only = 'reduce_only'


class LeverageType(ClassWithAttributes):
    cross = 'cross'
    isolated = 'isolated'


class PositionMode(ClassWithAttributes):
    one_way = 'one_way'
    hedge = 'hedge'


class PositionSide(ClassWithAttributes):
    both = 'both'
    long = 'long'
    short = 'short'


# Sides
BUY = 0
SELL = 1
