from mst_gateway.connector.api.types import OrderSchema, BUY, SELL

ORDER_BOOK_PARAMS = [
    ('tbinance_spot', OrderSchema.exchange, None, False, None, None),
    ('tbinance_spot', OrderSchema.exchange, None, False, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, None, False, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, None, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.exchange, None, True, None, None),
    ('tbinance_spot', OrderSchema.exchange, None, True, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, None, True, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, None, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.exchange, BUY, False, None, None),
    ('tbinance_spot', OrderSchema.exchange, BUY, False, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, BUY, False, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, BUY, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.exchange, BUY, True, None, None),
    ('tbinance_spot', OrderSchema.exchange, BUY, True, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, BUY, True, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, BUY, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.exchange, SELL, False, None, None),
    ('tbinance_spot', OrderSchema.exchange, SELL, False, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, SELL, False, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, SELL, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.exchange, SELL, True, None, None),
    ('tbinance_spot', OrderSchema.exchange, SELL, True, 1.0, None),
    ('tbinance_spot', OrderSchema.exchange, SELL, True, None, 1.0),
    ('tbinance_spot', OrderSchema.exchange, SELL, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, None, False, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, None, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, None, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, None, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, None, True, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, None, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, None, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, None, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, False, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, True, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, BUY, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, False, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, True, None, None),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_cross, SELL, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, None, False, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, None, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, None, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, None, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, None, True, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, None, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, None, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, None, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, False, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, True, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, BUY, True, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, False, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, False, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, False, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, False, 1.0, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, True, None, None),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, True, 1.0, None),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, True, None, 1.0),
    ('tbinance_spot', OrderSchema.margin_isolated, SELL, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, None, False, None, None),
    ('tbinance_margin', OrderSchema.margin, None, False, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, None, False, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, None, False, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, None, True, None, None),
    ('tbinance_margin', OrderSchema.margin, None, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, None, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, None, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, BUY, False, None, None),
    ('tbinance_margin', OrderSchema.margin, BUY, False, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, BUY, False, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, BUY, False, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, BUY, True, None, None),
    ('tbinance_margin', OrderSchema.margin, BUY, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, BUY, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, BUY, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, SELL, False, None, None),
    ('tbinance_margin', OrderSchema.margin, SELL, False, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, SELL, False, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, SELL, False, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin, SELL, True, None, None),
    ('tbinance_margin', OrderSchema.margin, SELL, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin, SELL, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin, SELL, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, None, True, None, None),
    ('tbinance_margin', OrderSchema.margin_coin, None, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin_coin, None, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, None, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, False, None, None),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, False, 1.0, None),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, False, None, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, False, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, True, None, None),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, BUY, True, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, False, None, None),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, False, 1.0, None),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, False, None, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, False, 1.0, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, True, None, None),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, True, 1.0, None),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, True, None, 1.0),
    ('tbinance_margin', OrderSchema.margin_coin, SELL, True, 1.0, 1.0),
]


DEFAULT_ORDER_BOOK_MESSAGE = {
    OrderSchema.exchange: {
        'e': 'depthUpdate',
        'E': 1638958726119,
        's': 'BTCUSDT',
        'U': 3288887,
        'u': 3288893,
        'b': [
            ['50238.41000000', '0.00000000'],
            ['50235.76000000', '0.00995400'],
            ['50230.59000000', '0.00995500'],
        ],
        'a': [
            ['50245.03000000', '0.00995200'],
            ['50249.10000000', '0.00000000'],
            ['50252.50000000', '0.00995000'],
            ['50266.42000000', '0.00000000'],
        ],
    },
    OrderSchema.margin: {
        'e': 'depthUpdate',
        'E': 1638963965447,
        'T': 1638963965439,
        's': 'BTCUSDT',
        'U': 23138568456,
        'u': 23138568515,
        'pu': 23138568440,
        'b': [
            ['48982.80', '0.000'],
            ['49033.90', '0.000'],
            ['49058.78', '0.020'],
            ['49087.77', '0.010'],
        ],
        'a': [['49329.52', '0.010'], ['49353.42', '0.040']],
    },
    OrderSchema.margin_coin: {
        'e': 'depthUpdate',
        'E': 1638963974916,
        'T': 1638963974726,
        's': 'BTCUSD_PERP',
        'ps': 'BTCUSD',
        'U': 2091967181,
        'u': 2091967184,
        'pu': 2091967180,
        'b': [['49219.7', '0.020']],
        'a': [['49242.9', '0'], ['49244.9', '0'], ['49245.9', '0.010']],
    },
}
DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': 'depthUpdate',
        'action': 'update',
        'data': [
            {
                'e': 'depthUpdate',
                'E': 1638958726119,
                's': 'BTCUSDT',
                'U': 3288887,
                'u': 3288893,
                'b': [
                    ['50238.41000000', '0.00000000'],
                    ['50235.76000000', '0.00995400'],
                    ['50230.59000000', '0.00995500'],
                ],
                'a': [
                    ['50245.03000000', '0.00995200'],
                    ['50249.10000000', '0.00000000'],
                    ['50252.50000000', '0.00995000'],
                    ['50266.42000000', '0.00000000'],
                ],
            }
        ],
    },
    OrderSchema.margin: {
        'table': 'depthUpdate',
        'action': 'update',
        'data': [
            {
                'e': 'depthUpdate',
                'E': 1638963965447,
                'T': 1638963965439,
                's': 'BTCUSDT',
                'U': 23138568456,
                'u': 23138568515,
                'pu': 23138568440,
                'b': [
                    ['48982.80', '0.000'],
                    ['49033.90', '0.000'],
                    ['49058.78', '0.020'],
                    ['49087.77', '0.010'],
                ],
                'a': [['49329.52', '0.010'], ['49353.42', '0.040']],
            }
        ],
    },
    OrderSchema.margin_coin: {
        'table': 'depthUpdate',
        'action': 'update',
        'data': [
            {
                'e': 'depthUpdate',
                'E': 1638963974916,
                'T': 1638963974726,
                's': 'BTCUSD_PERP',
                'ps': 'BTCUSD',
                'U': 2091967181,
                'u': 2091967184,
                'pu': 2091967180,
                'b': [['49219.7', '0.020']],
                'a': [['49242.9', '0'], ['49244.9', '0'], ['49245.9', '0.010']],
            }
        ],
    },
}
DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': 'depthUpdate',
            'action': 'delete',
            'data': [
                {
                    'b': ['50238.41000000', '0.00000000'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
                {
                    'a': ['50249.10000000', '0.00000000'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
                {
                    'a': ['50266.42000000', '0.00000000'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
            ],
        },
        {
            'table': 'depthUpdate',
            'action': 'update',
            'data': [
                {
                    'b': ['50235.76000000', '0.00995400'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
                {
                    'b': ['50230.59000000', '0.00995500'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
                {
                    'a': ['50245.03000000', '0.00995200'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
                {
                    'a': ['50252.50000000', '0.00995000'],
                    'e': 'depthUpdate',
                    'E': 1638958726119,
                    's': 'BTCUSDT',
                    'U': 3288887,
                    'u': 3288893,
                },
            ],
        },
    ],
    OrderSchema.margin: [
        {
            'table': 'depthUpdate',
            'action': 'delete',
            'data': [
                {
                    'b': ['48982.80', '0.000'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
                {
                    'b': ['49033.90', '0.000'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
            ],
        },
        {
            'table': 'depthUpdate',
            'action': 'update',
            'data': [
                {
                    'b': ['49058.78', '0.020'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
                {
                    'b': ['49087.77', '0.010'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
                {
                    'a': ['49329.52', '0.010'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
                {
                    'a': ['49353.42', '0.040'],
                    'e': 'depthUpdate',
                    'E': 1638963965447,
                    'T': 1638963965439,
                    's': 'BTCUSDT',
                    'U': 23138568456,
                    'u': 23138568515,
                    'pu': 23138568440,
                },
            ],
        },
    ],
    OrderSchema.margin_coin: [
        {
            'table': 'depthUpdate',
            'action': 'delete',
            'data': [
                {
                    'a': ['49242.9', '0'],
                    'e': 'depthUpdate',
                    'E': 1638963974916,
                    'T': 1638963974726,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'U': 2091967181,
                    'u': 2091967184,
                    'pu': 2091967180,
                },
                {
                    'a': ['49244.9', '0'],
                    'e': 'depthUpdate',
                    'E': 1638963974916,
                    'T': 1638963974726,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'U': 2091967181,
                    'u': 2091967184,
                    'pu': 2091967180,
                },
            ],
        },
        {
            'table': 'depthUpdate',
            'action': 'update',
            'data': [
                {
                    'b': ['49219.7', '0.020'],
                    'e': 'depthUpdate',
                    'E': 1638963974916,
                    'T': 1638963974726,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'U': 2091967181,
                    'u': 2091967184,
                    'pu': 2091967180,
                },
                {
                    'a': ['49245.9', '0.010'],
                    'e': 'depthUpdate',
                    'E': 1638963974916,
                    'T': 1638963974726,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'U': 2091967181,
                    'u': 2091967184,
                    'pu': 2091967180,
                },
            ],
        },
    ],
}
DEFAULT_ORDER_BOOK_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'order_book': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'order_book',
                'sch': 'exchange',
                'act': 'delete',
                'd': [
                    {
                        'id': 5023841,
                        's': 'btcusdt',
                        'p': 50238.41,
                        'vl': 0.0,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 5024910,
                        's': 'btcusdt',
                        'p': 50249.1,
                        'vl': 0.0,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 5026642,
                        's': 'btcusdt',
                        'p': 50266.42,
                        'vl': 0.0,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                ],
            }
        },
        {
            'order_book': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'order_book',
                'sch': 'exchange',
                'act': 'update',
                'd': [
                    {
                        'id': 5023576,
                        's': 'btcusdt',
                        'p': 50235.76,
                        'vl': 0.009954,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 5023059,
                        's': 'btcusdt',
                        'p': 50230.59,
                        'vl': 0.009955,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 5024503,
                        's': 'btcusdt',
                        'p': 50245.03,
                        'vl': 0.009952,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 5025250,
                        's': 'btcusdt',
                        'p': 50252.5,
                        'vl': 0.00995,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                ],
            }
        },
    ],
    OrderSchema.margin: [
        {
            'order_book': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'order_book',
                'sch': OrderSchema.margin,
                'act': 'delete',
                'd': [
                    {
                        'id': 489828,
                        's': 'btcusdt',
                        'p': 48982.8,
                        'vl': 0.0,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 490339,
                        's': 'btcusdt',
                        'p': 49033.9,
                        'vl': 0.0,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                ],
            }
        },
        {
            'order_book': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'order_book',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'id': 490587,
                        's': 'btcusdt',
                        'p': 49058.78,
                        'vl': 0.02,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 490877,
                        's': 'btcusdt',
                        'p': 49087.77,
                        'vl': 0.01,
                        'sd': 0,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 493295,
                        's': 'btcusdt',
                        'p': 49329.52,
                        'vl': 0.01,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                    {
                        'id': 493534,
                        's': 'btcusdt',
                        'p': 49353.42,
                        'vl': 0.04,
                        'sd': 1,
                        'ss': 'btcusdt',
                    },
                ],
            }
        },
    ],
    OrderSchema.margin_coin: [
        {
            'order_book': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'order_book',
                'sch': 'margin_coin',
                'act': 'delete',
                'd': [
                    {
                        'id': 492429,
                        's': 'btcusd_perp',
                        'p': 49242.9,
                        'vl': 0.0,
                        'sd': 1,
                        'ss': 'btcusd',
                    },
                    {
                        'id': 492449,
                        's': 'btcusd_perp',
                        'p': 49244.9,
                        'vl': 0.0,
                        'sd': 1,
                        'ss': 'btcusd',
                    },
                ],
            }
        },
        {
            'order_book': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'order_book',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'id': 492196,
                        's': 'btcusd_perp',
                        'p': 49219.7,
                        'vl': 0.02,
                        'sd': 0,
                        'ss': 'btcusd',
                    },
                    {
                        'id': 492459,
                        's': 'btcusd_perp',
                        'p': 49245.9,
                        'vl': 0.01,
                        'sd': 1,
                        'ss': 'btcusd',
                    },
                ],
            }
        },
    ],
}
