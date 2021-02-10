from mst_gateway.connector.api.stocks.bitmex.utils import to_date


STORAGE_DATA = {
    'symbol': {
        'bitmex': {
            'margin1': {
                'ethusd': {
                    'tick': 0.05,
                    'volume_tick': 1.0,
                    'pair': [
                        'ETH',
                        'USD'
                    ],
                    'expiration': None,
                    'schema': 'margin1',
                    'symbol_schema': 'margin1',
                    'system_symbol': 'ethusd',
                    'symbol': 'ethusd',
                    'exchange': 'Bitmex',
                    'created': to_date('2020-06-25T13:03:00.295118Z'),
                    'max_leverage': 50.0,
                },
                'xbtusd': {
                    'tick': 0.5,
                    'volume_tick': 1.0,
                    'pair': [
                        'XBT',
                        'USD'
                    ],
                    'expiration': None,
                    'schema': 'margin1',
                    'symbol_schema': 'margin1',
                    'system_symbol': 'btcusd',
                    'symbol': 'xbtusd',
                    'exchange': 'Bitmex',
                    'created': to_date('2020-06-25T13:03:00.295118Z'),
                    'max_leverage': 100.0,
                }
            }
        },
        'tbitmex': {
            'margin1': {
                'ethusd': {
                    'tick': 0.05,
                    'volume_tick': 1.0,
                    'pair': [
                        'ETH',
                        'USD'
                    ],
                    'expiration': None,
                    'schema': 'margin1',
                    'symbol_schema': 'margin1',
                    'system_symbol': 'ethusd',
                    'symbol': 'ethusd',
                    'exchange': 'tBitmex',
                    'created':  to_date('2020-06-25T13:03:00.295118Z'),
                    'max_leverage': 50.0,
                },
                'xbtusd': {
                    'tick': 0.5,
                    'volume_tick': 1.0,
                    'pair': [
                        'XBT',
                        'USD'
                    ],
                    'expiration': None,
                    'schema': 'margin1',
                    'symbol_schema': 'margin1',
                    'system_symbol': 'btcusd',
                    'symbol': 'xbtusd',
                    'exchange': 'tBitmex',
                    'created':  to_date('2020-06-25T13:03:00.295118Z'),
                    'max_leverage': 100.0,
                }
            }
        }
    }
}
