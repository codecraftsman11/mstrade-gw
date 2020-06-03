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


class OrderSchema(ClassWithAttributes):
    margin1 = 'margin1'
    margin2 = 'margin2'
    futures = 'futures'
    exchange = 'exchange'


class OrderState(ClassWithAttributes):
    waiting = 'waiting'         # Algorithm is waiting for start
    started = 'started'         # Algorithm is strarted
    canceled = 'canceled'       # Algorithm is canceled
    pending = 'pending'         # Limit order is waiting to activate
    deleted = 'deleted'         # Limit order is deleted
    active = 'active'           # Limit Order is activated
    closed = 'closed'           # Active order is closed
    liquidated = 'liquidated'   # Active order is liquidated


class OrderTTL(ClassWithAttributes):
    GTC = 'GTC'
    H1 = 'H1'
    H4 = 'H4'
    D1 = 'D1'


class OrderExec(ClassWithAttributes):
    market = 'market'
    limit = 'limit'


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

# Sides
BUY = 0
SELL = 1
