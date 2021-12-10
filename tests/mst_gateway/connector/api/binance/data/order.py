from mst_gateway.connector.api.types import OrderExec, OrderSchema, OrderType, OrderTTL, BUY, SELL

DEFAULT_ORDER_SIDE = BUY
DEFAULT_ORDER_SIDE_STR = 'BUY'
DEFAULT_ORDER_OPPOSITE_SIDE = SELL
DEFAULT_ORDER_OPPOSITE_SIDE_STR = 'SELL'
DEFAULT_ORDER_VOLUME = {
    OrderSchema.exchange: 0.001,
    OrderSchema.futures: 0.001,
    OrderSchema.futures_coin: 1.0,
}
DEFAULT_ORDER_OPTIONS = {
    'ttl': OrderTTL.GTC,
    'is_passive': False,
    'is_iceberg': False,
    'iceberg_volume': None,
    'comments': '',
}
DEFAULT_ORDER = {
    OrderSchema.exchange: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.exchange,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSDT',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
    },
    OrderSchema.futures: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.futures,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSDT',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.futures],
    },
    OrderSchema.futures_coin: {
        'active': False,
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.futures_coin,
        'side': DEFAULT_ORDER_SIDE_STR,
        'stop': 0.0,
        'symbol': 'BTCUSD_PERP',
        'system_symbol': 'btcusd',
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
    },
}

DEFAULT_ORDER_MESSAGE = {
    OrderSchema.exchange: {
        'e': 'executionReport',
        'E': 1639057750403,
        's': 'BTCUSDT',
        'c': 'VuuQ6CA63KWGl7Qyq9GFCR',
        'S': 'BUY',
        'o': 'LIMIT',
        'f': 'GTC',
        'q': '0.00100000',
        'p': '49200.00000000',
        'P': '0.00000000',
        'F': '0.00000000',
        'g': -1,
        'C': '',
        'x': 'NEW',
        'X': 'NEW',
        'r': 'NONE',
        'i': 2352852,
        'l': '0.00000000',
        'z': '0.00000000',
        'L': '0.00000000',
        'n': '0',
        'N': None,
        'T': 1639057750402,
        't': -1,
        'I': 5210446,
        'w': True,
        'm': False,
        'M': False,
        'O': 1639057750402,
        'Z': '0.00000000',
        'Y': '0.00000000',
        'Q': '0.00000000',
    },
    OrderSchema.futures: {
        'e': 'ORDER_TRADE_UPDATE',
        'T': 1639058196458,
        'E': 1639058196460,
        'o': {
            's': 'BTCUSDT',
            'c': 'web_PqSHEF5jz9kgqy9Ql82X',
            'S': 'BUY',
            'o': 'LIMIT',
            'f': 'GTC',
            'q': '0.001',
            'p': '49328.01',
            'ap': '0',
            'sp': '0',
            'x': 'NEW',
            'X': 'NEW',
            'i': 2939862341,
            'l': '0',
            'z': '0',
            'L': '0',
            'T': 1639058196458,
            't': 0,
            'b': '0',
            'a': '0',
            'm': False,
            'R': False,
            'wt': 'CONTRACT_PRICE',
            'ot': 'LIMIT',
            'ps': 'BOTH',
            'cp': False,
            'rp': '0',
            'pP': False,
            'si': 0,
            'ss': 0,
        },
    },
    OrderSchema.futures_coin: {
        'e': 'ORDER_TRADE_UPDATE',
        'T': 1639058394216,
        'E': 1639058394219,
        'i': 'SgsRoCSgAusR',
        'o': {
            's': 'BTCUSD_PERP',
            'c': 'web_UPJWJK4WYHUUQepbVPFl',
            'S': 'BUY',
            'o': 'LIMIT',
            'f': 'GTC',
            'q': '1',
            'p': '49400.8',
            'ap': '0',
            'sp': '0',
            'x': 'NEW',
            'X': 'NEW',
            'i': 229157580,
            'l': '0',
            'z': '0',
            'L': '0',
            'T': 1639058394216,
            't': 0,
            'b': '0',
            'a': '0',
            'm': False,
            'R': False,
            'wt': 'CONTRACT_PRICE',
            'ot': 'LIMIT',
            'ps': 'BOTH',
            'cp': False,
            'ma': 'BTC',
            'rp': '0',
            'pP': False,
            'si': 0,
            'ss': 0,
        },
    },
}
DEFAULT_ORDER_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': 'executionReport',
        'action': 'update',
        'data': [
            {
                'e': 'executionReport',
                'E': 1639057750403,
                's': 'BTCUSDT',
                'c': 'VuuQ6CA63KWGl7Qyq9GFCR',
                'S': 'BUY',
                'o': 'LIMIT',
                'f': 'GTC',
                'q': '0.00100000',
                'p': '49200.00000000',
                'P': '0.00000000',
                'F': '0.00000000',
                'g': -1,
                'C': '',
                'x': 'NEW',
                'X': 'NEW',
                'r': 'NONE',
                'i': 2352852,
                'l': '0.00000000',
                'z': '0.00000000',
                'L': '0.00000000',
                'n': '0',
                'N': None,
                'T': 1639057750402,
                't': -1,
                'I': 5210446,
                'w': True,
                'm': False,
                'M': False,
                'O': 1639057750402,
                'Z': '0.00000000',
                'Y': '0.00000000',
                'Q': '0.00000000',
            }
        ],
    },
    OrderSchema.futures: {
        'table': 'ORDER_TRADE_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ORDER_TRADE_UPDATE',
                'T': 1639058196458,
                'E': 1639058196460,
                'o': {
                    's': 'BTCUSDT',
                    'c': 'web_PqSHEF5jz9kgqy9Ql82X',
                    'S': 'BUY',
                    'o': 'LIMIT',
                    'f': 'GTC',
                    'q': '0.001',
                    'p': '49328.01',
                    'ap': '0',
                    'sp': '0',
                    'x': 'NEW',
                    'X': 'NEW',
                    'i': 2939862341,
                    'l': '0',
                    'z': '0',
                    'L': '0',
                    'T': 1639058196458,
                    't': 0,
                    'b': '0',
                    'a': '0',
                    'm': False,
                    'R': False,
                    'wt': 'CONTRACT_PRICE',
                    'ot': 'LIMIT',
                    'ps': 'BOTH',
                    'cp': False,
                    'rp': '0',
                    'pP': False,
                    'si': 0,
                    'ss': 0,
                },
            }
        ],
    },
    OrderSchema.futures_coin: {
        'table': 'ORDER_TRADE_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ORDER_TRADE_UPDATE',
                'T': 1639058394216,
                'E': 1639058394219,
                'i': 'SgsRoCSgAusR',
                'o': {
                    's': 'BTCUSD_PERP',
                    'c': 'web_UPJWJK4WYHUUQepbVPFl',
                    'S': 'BUY',
                    'o': 'LIMIT',
                    'f': 'GTC',
                    'q': '1',
                    'p': '49400.8',
                    'ap': '0',
                    'sp': '0',
                    'x': 'NEW',
                    'X': 'NEW',
                    'i': 229157580,
                    'l': '0',
                    'z': '0',
                    'L': '0',
                    'T': 1639058394216,
                    't': 0,
                    'b': '0',
                    'a': '0',
                    'm': False,
                    'R': False,
                    'wt': 'CONTRACT_PRICE',
                    'ot': 'LIMIT',
                    'ps': 'BOTH',
                    'cp': False,
                    'ma': 'BTC',
                    'rp': '0',
                    'pP': False,
                    'si': 0,
                    'ss': 0,
                },
            }
        ],
    },
}
DEFAULT_ORDER_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': 'executionReport',
            'action': 'insert',
            'data': [
                {
                    'e': 'executionReport',
                    'E': 1639057750403,
                    's': 'BTCUSDT',
                    'c': 'VuuQ6CA63KWGl7Qyq9GFCR',
                    'S': 'BUY',
                    'o': 'LIMIT',
                    'f': 'GTC',
                    'q': '0.00100000',
                    'p': '49200.00000000',
                    'P': '0.00000000',
                    'F': '0.00000000',
                    'g': -1,
                    'C': '',
                    'x': 'NEW',
                    'X': 'NEW',
                    'r': 'NONE',
                    'i': 2352852,
                    'l': '0.00000000',
                    'z': '0.00000000',
                    'L': '0.00000000',
                    'n': '0',
                    'N': None,
                    'T': 1639057750402,
                    't': -1,
                    'I': 5210446,
                    'w': True,
                    'm': False,
                    'M': False,
                    'O': 1639057750402,
                    'Z': '0.00000000',
                    'Y': '0.00000000',
                    'Q': '0.00000000',
                }
            ],
        }
    ],
    OrderSchema.futures: [
        {
            'table': 'ORDER_TRADE_UPDATE',
            'action': 'insert',
            'data': [
                {
                    'e': 'ORDER_TRADE_UPDATE',
                    'T': 1639058196458,
                    'E': 1639058196460,
                    's': 'BTCUSDT',
                    'c': 'web_PqSHEF5jz9kgqy9Ql82X',
                    'S': 'BUY',
                    'o': 'LIMIT',
                    'f': 'GTC',
                    'q': '0.001',
                    'p': '49328.01',
                    'ap': '0',
                    'sp': '0',
                    'x': 'NEW',
                    'X': 'NEW',
                    'i': 2939862341,
                    'l': '0',
                    'z': '0',
                    'L': '0',
                    't': 0,
                    'b': '0',
                    'a': '0',
                    'm': False,
                    'R': False,
                    'wt': 'CONTRACT_PRICE',
                    'ot': 'LIMIT',
                    'ps': 'BOTH',
                    'cp': False,
                    'rp': '0',
                    'pP': False,
                    'si': 0,
                    'ss': 0,
                }
            ],
        }
    ],
    OrderSchema.futures_coin: [
        {
            'table': 'ORDER_TRADE_UPDATE',
            'action': 'insert',
            'data': [
                {
                    'e': 'ORDER_TRADE_UPDATE',
                    'T': 1639058394216,
                    'E': 1639058394219,
                    'i': 229157580,
                    's': 'BTCUSD_PERP',
                    'c': 'web_UPJWJK4WYHUUQepbVPFl',
                    'S': 'BUY',
                    'o': 'LIMIT',
                    'f': 'GTC',
                    'q': '1',
                    'p': '49400.8',
                    'ap': '0',
                    'sp': '0',
                    'x': 'NEW',
                    'X': 'NEW',
                    'l': '0',
                    'z': '0',
                    'L': '0',
                    't': 0,
                    'b': '0',
                    'a': '0',
                    'm': False,
                    'R': False,
                    'wt': 'CONTRACT_PRICE',
                    'ot': 'LIMIT',
                    'ps': 'BOTH',
                    'cp': False,
                    'ma': 'BTC',
                    'rp': '0',
                    'pP': False,
                    'si': 0,
                    'ss': 0,
                }
            ],
        }
    ],
}
DEFAULT_ORDER_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        None
    ],
    OrderSchema.futures: [
        None
    ],
    OrderSchema.futures_coin: [
        None
    ],
}
