from mst_gateway.utils import ClassWithAttributes


class OrderType(ClassWithAttributes):
    market = 'market'
    limit = 'limit'
    stop_loss = 'stop_loss'
    take_profit = 'take_profit'
    noloss = 'noloss'
    trailing_stop = 'trailing_stop'
    trailing_trigger_stop = 'trailing_trigger_stop'
    box_top = 'box_top'
    limit_turn = 'limit_turn'
    stop_turn = 'stop_turn'
    squeeze = 'squeeze'
    limit_smart = 'limit_smart'
    position = 'position'


class OrderSchema(ClassWithAttributes):
    margin1 = 'margin1'
    margin2 = 'margin2'
    margin3 = 'margin3'
    futures = 'futures'
    exchange = 'exchange'
    futures_coin = 'futures_coin'


class OrderSchemaTradeMode(ClassWithAttributes):
    margin1 = ['margin1']
    margin2 = ['margin2']
    margin3 = ['margin3']
    futures = ['futures']
    exchange = ['trade', 'exchange']
    futures_coin = ['futures_coin']

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
    started = 'started'         # Algorithm is strarted
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
    H1 = 'H1'
    H4 = 'H4'
    D1 = 'D1'


class OrderExec(ClassWithAttributes):
    market = 'market'
    limit = 'limit'


class OrderParams(ClassWithAttributes):
    iceberg = 'iceberg'
    passive = 'passive'
    post_only = 'post_only'
    reduce_only = 'reduce_only'


class OrderPositionPeriod(ClassWithAttributes):
    M1 = 'M1'
    M15 = 'M15'
    M30 = 'M30'
    H1 = 'H1'
    H4 = 'H4'
    D1 = 'D1'


class OrderPositionTrendType(ClassWithAttributes):
    direct = 'direct'
    opposite = 'opposite'
    flat = 'flat'


class OrderPositionOpenedBy(ClassWithAttributes):
    limit = 'limit'
    market = 'market'
    box_top = 'box_top'
    limit_turn = 'limit_turn'
    stop_turn = 'stop_turn'
    squeeze = 'squeeze'
    limit_smart = 'limit_smart'


class OrderPositionClosedBy(ClassWithAttributes):
    take_profit = 'take_profit'
    stop_loss = 'stop_loss'
    market = 'market'
    liquidation = 'liquidation'
    noloss = 'noloss'
    trailing_stop = 'trailing_stop'


class OrderStandardTypes(ClassWithAttributes):
    limit = OrderType.limit
    market = OrderType.market


class LeverageType(ClassWithAttributes):
    cross = 'cross'
    isolated = 'isolated'


ORDER_STANDARD_TYPES = (
    OrderType.limit,
    OrderType.market,
)


ORDER_ALGORITHM_TYPES = (
    OrderType.box_top,
    OrderType.limit_turn,
    OrderType.stop_turn,
    OrderType.squeeze,
    OrderType.limit_smart
)


ORDER_OPEN_TYPES = (
    OrderType.limit,
    OrderType.market,
    OrderType.box_top,
    OrderType.limit_turn,
    OrderType.stop_turn,
    OrderType.squeeze,
    OrderType.limit_smart
)


ORDER_CLOSE_TYPES = (
    OrderType.stop_loss,
    OrderType.take_profit,
    OrderType.noloss,
    OrderType.trailing_stop,
    OrderType.trailing_trigger_stop
)


ORDER_POSITION_TYPES = (
    OrderType.position,
)

# Sides
BUY = 0
SELL = 1
