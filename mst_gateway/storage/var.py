from mst_gateway.utils import ClassWithAttributes


class StateStorageKey(ClassWithAttributes):
    symbol = 'data:symbol'
    system_symbol = 'data:system_symbol'
    exchange_rates = 'data:exchange_rates'
    funding_rates = 'data:funding_rates'
    throttling = 'throttling'
    state = 'state'


THROTTLE_LIMITS = {
    'tbinance': {
        'ws': 30,
        'rest': 1000,
        'order': 100
    },
    'binance': {
        'ws': 60,
        'rest': 1000,
        'order': 100
    },
    'tbitmex': {
        'ws': 50,
        'rest': 100,
        'order': 10
    },
    'bitmex': {
        'ws': 50,
        'rest': 100,
        'order': 10
    }
}
