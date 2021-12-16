from mst_gateway.connector.api.types import OrderSchema

DEFAULT_TRADE_MESSAGE = {
    OrderSchema.exchange: {
        'e': 'trade',
        'E': 1638958928243,
        's': 'BTCUSDT',
        't': 459568,
        'p': '50229.54000000',
        'q': '0.00995500',
        'b': 1906624,
        'a': 1906608,
        'T': 1638958928242,
        'm': False,
        'M': True,
    },
    OrderSchema.futures: {
        'e': 'trade',
        'E': 1638963971897,
        'T': 1638963971895,
        's': 'BTCUSDT',
        't': 217093309,
        'p': '49145.63',
        'q': '0.010',
        'X': 'MARKET',
        'm': True,
    },
    OrderSchema.futures_coin: {
        'e': 'trade',
        'E': 1638965335074,
        'T': 1638965335062,
        's': 'BTCUSD_PERP',
        't': 50097309,
        'p': '49222.5',
        'q': '1',
        'X': 'MARKET',
        'm': False,
    },
}
DEFAULT_TRADE_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': 'trade',
        'action': 'update',
        'data': [
            {
                'e': 'trade',
                'E': 1638958928243,
                's': 'BTCUSDT',
                't': 459568,
                'p': '50229.54000000',
                'q': '0.00995500',
                'b': 1906624,
                'a': 1906608,
                'T': 1638958928242,
                'm': False,
                'M': True,
            }
        ],
    },
    OrderSchema.futures: {
        'table': 'trade',
        'action': 'update',
        'data': [
            {
                'e': 'trade',
                'E': 1638963971897,
                'T': 1638963971895,
                's': 'BTCUSDT',
                't': 217093309,
                'p': '49145.63',
                'q': '0.010',
                'X': 'MARKET',
                'm': True,
            }
        ],
    },
    OrderSchema.futures_coin: {
        'table': 'trade',
        'action': 'update',
        'data': [
            {
                'e': 'trade',
                'E': 1638965335074,
                'T': 1638965335062,
                's': 'BTCUSD_PERP',
                't': 50097309,
                'p': '49222.5',
                'q': '1',
                'X': 'MARKET',
                'm': False,
            }
        ],
    },
}
DEFAULT_TRADE_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': 'trade',
            'action': 'update',
            'data': [
                {
                    'e': 'trade',
                    'E': 1638958928243,
                    's': 'BTCUSDT',
                    't': 459568,
                    'p': '50229.54000000',
                    'q': '0.00995500',
                    'b': 1906624,
                    'a': 1906608,
                    'T': 1638958928242,
                    'm': False,
                    'M': True,
                }
            ],
        }
    ],
    OrderSchema.futures: [
        {
            'table': 'trade',
            'action': 'update',
            'data': [
                {
                    'e': 'trade',
                    'E': 1638963971897,
                    'T': 1638963971895,
                    's': 'BTCUSDT',
                    't': 217093309,
                    'p': '49145.63',
                    'q': '0.010',
                    'X': 'MARKET',
                    'm': True,
                }
            ],
        }
    ],
    OrderSchema.futures_coin: [
        {
            'table': 'trade',
            'action': 'update',
            'data': [
                {
                    'e': 'trade',
                    'E': 1638965335074,
                    'T': 1638965335062,
                    's': 'BTCUSD_PERP',
                    't': 50097309,
                    'p': '49222.5',
                    'q': '1',
                    'X': 'MARKET',
                    'm': False,
                }
            ],
        }
    ],
}
DEFAULT_TRADE_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'trade': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'trade',
                'sch': 'exchange',
                'act': 'insert',
                'd': [
                    {
                        'tm': '2021-12-08T10:22:08.243000',
                        'p': 50229.54,
                        'vl': 0.009955,
                        'sd': 1,
                        's': 'BTCUSDT',
                        'ss': 'btcusd',
                    }
                ],
            }
        }
    ],
    OrderSchema.futures: [
        {
            'trade': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'trade',
                'sch': 'futures',
                'act': 'insert',
                'd': [
                    {
                        'tm': '2021-12-08T11:46:11.897000',
                        'p': 49145.63,
                        'vl': 0.01,
                        'sd': 0,
                        's': 'BTCUSDT',
                        'ss': 'btcusd',
                    }
                ],
            }
        }
    ],
    OrderSchema.futures_coin: [
        {
            'trade': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'trade',
                'sch': 'futures_coin',
                'act': 'insert',
                'd': [
                    {
                        'tm': '2021-12-08T12:08:55.074000',
                        'p': 49222.5,
                        'vl': 1.0,
                        'sd': 1,
                        's': 'BTCUSD_PERP',
                        'ss': 'btcusd',
                    }
                ],
            }
        }
    ],
}
