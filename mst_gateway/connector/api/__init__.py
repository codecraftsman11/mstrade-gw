# pylint: disable=broad-except
from importlib import import_module
from ...utils import ClassWithAttributes

# Sides
BUY = 0
SELL = 1


# Order Types
class OrderType(ClassWithAttributes):
    market = 'market'
    limit = 'limit'
    sl_market = 'sl_market'
    sl_limit = 'sl_limit'
    tp_market = 'tp_market'
    tp_limit = 'tp_limit'
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
    trade = 'trade'
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


ALGORITHM_ORDER_TYPES = (
    OrderType.box_top,
    OrderType.limit_turn,
    OrderType.stop_turn,
    OrderType.squeeze,
    OrderType.limit_smart
)


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
DATETIME_OUT_FORMAT = "%Y-%m-%d %H:%M:%S.%fZ"


def init(params: dict, auth=None, cls=None, logger=None):
    cls = cls or import_module('.stocks.bitmex.rest',
                               package=__package__).BitmexRestApi
    return cls(url=params.get('url', None), auth=auth, logger=logger)


def connect(params, auth, cls=None, logger=None):
    connector = init(params, auth, cls, logger)
    if auth:
        return connector.connect()
    return connector
