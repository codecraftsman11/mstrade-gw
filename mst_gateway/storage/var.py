from mst_gateway.utils import ClassWithAttributes


class StateStorageKey(ClassWithAttributes):
    symbol = 'data:symbol'
    system_symbol = 'data:system_symbol'
    currency = 'data:currency'
    exchange_rates = 'data:exchange_rates'
    funding_rates = 'data:funding_rates'
    throttling = 'throttling'
    state = 'state'
