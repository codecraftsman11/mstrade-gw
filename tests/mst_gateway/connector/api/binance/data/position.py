from mst_gateway.connector.api.types import OrderSchema, LeverageType

DEFAULT_POSITIONS_STATE = {
    OrderSchema.futures: {
        'btcusdt': {
            'action': 'update',
            'cross_wallet_balance': 99760.41099324,
            'entry_price': 57000.0,
            'isolated_wallet_balance': 100000.0,
            'leverage': 1.0,
            'leverage_type': LeverageType.cross,
            'mark_price': 56900.,
            'side': 1,
            'symbol': 'btcusdt',
            'volume': 0.001,
        },
    },
    OrderSchema.futures_coin: {
        'btcusd_perp': {
            'action': 'update',
            'cross_wallet_balance': 99760.41099324,
            'entry_price': 57000.0,
            'isolated_wallet_balance': 100000.0,
            'leverage': 1.0,
            'leverage_type': LeverageType.isolated,
            'mark_price': 56900.0,
            'side': 1,
            'symbol': 'btcusd_perp',
            'volume': 0.001,
        },
    }
}


DEFAULT_POSITION_MESSAGE = {
    OrderSchema.exchange: [
        {
            'e': '24hrTicker',
            'E': 1638964424515,
            's': 'BTCUSDT',
            'p': '-2214.54000000',
            'P': '-4.311',
            'w': '46897.67609538',
            'x': '51373.17000000',
            'c': '49155.42000000',
            'Q': '0.01000000',
            'b': '49152.96000000',
            'B': '0.01017300',
            'a': '49152.97000000',
            'A': '0.01017300',
            'o': '51369.96000000',
            'h': '120000.00000000',
            'l': '9782.00000000',
            'v': '1038.52459100',
            'q': '48704389.88580066',
            'O': 1638878022537,
            'C': 1638964422537,
            'F': 381050,
            'L': 466268,
            'n': 85219,
        }
    ],
    OrderSchema.futures: {
        'e': 'ACCOUNT_UPDATE',
        'T': 1639058196458,
        'E': 1639058196460,
        'a': {
            'B': [
                {'a': 'USDT', 'wb': '9999.96949206', 'cw': '9950.66684270', 'bc': '0'}
            ],
            'P': [
                {
                    's': 'BTCUSDT',
                    'pa': '0.001',
                    'ep': '49294.07000',
                    'cr': '-3973.10941998',
                    'up': '0.00564300',
                    'mt': 'isolated',
                    'iw': '49.30264936',
                    'ps': 'BOTH',
                    'ma': 'USDT',
                }
            ],
            'm': 'ORDER',
        },
    },
    OrderSchema.futures_coin: {
        'e': 'ACCOUNT_UPDATE',
        'T': 1639058394216,
        'E': 1639058394219,
        'i': 'SgsRoCSgAusR',
        'a': {
            'B': [
                {'a': 'BTC', 'wb': '9.99965786', 'cw': '9.99965786', 'bc': '0'},
                {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
            ],
            'P': [
                {
                    's': 'BTCUSD_PERP',
                    'pa': '1',
                    'ep': '49383.5',
                    'cr': '-0.00018150',
                    'up': '0.00000003',
                    'mt': 'cross',
                    'iw': '0',
                    'ps': 'BOTH',
                    'ma': 'BTC',
                }
            ],
            'm': 'ORDER',
        },
    },
}
DEFAULT_POSITION_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638964424515,
                's': 'BTCUSDT',
                'p': '-2214.54000000',
                'P': '-4.311',
                'w': '46897.67609538',
                'x': '51373.17000000',
                'c': '49155.42000000',
                'Q': '0.01000000',
                'b': '49152.96000000',
                'B': '0.01017300',
                'a': '49152.97000000',
                'A': '0.01017300',
                'o': '51369.96000000',
                'h': '120000.00000000',
                'l': '9782.00000000',
                'v': '1038.52459100',
                'q': '48704389.88580066',
                'O': 1638878022537,
                'C': 1638964422537,
                'F': 381050,
                'L': 466268,
                'n': 85219,
            }
        ],
    },
    OrderSchema.futures: {
        'table': 'ACCOUNT_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ACCOUNT_UPDATE',
                'T': 1639058196458,
                'E': 1639058196460,
                'a': {
                    'B': [
                        {
                            'a': 'USDT',
                            'wb': '9999.96949206',
                            'cw': '9950.66684270',
                            'bc': '0',
                        }
                    ],
                    'P': [
                        {
                            's': 'BTCUSDT',
                            'pa': '0.001',
                            'ep': '49294.07000',
                            'cr': '-3973.10941998',
                            'up': '0.00564300',
                            'mt': 'isolated',
                            'iw': '49.30264936',
                            'ps': 'BOTH',
                            'ma': 'USDT',
                        }
                    ],
                    'm': 'ORDER',
                },
            }
        ],
    },
    OrderSchema.futures_coin: {
        'table': 'ACCOUNT_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ACCOUNT_UPDATE',
                'T': 1639058394216,
                'E': 1639058394219,
                'i': 'SgsRoCSgAusR',
                'a': {
                    'B': [
                        {'a': 'BTC', 'wb': '9.99965786', 'cw': '9.99965786', 'bc': '0'},
                        {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                    ],
                    'P': [
                        {
                            's': 'BTCUSD_PERP',
                            'pa': '1',
                            'ep': '49383.5',
                            'cr': '-0.00018150',
                            'up': '0.00000003',
                            'mt': 'cross',
                            'iw': '0',
                            'ps': 'BOTH',
                            'ma': 'BTC',
                        }
                    ],
                    'm': 'ORDER',
                },
            }
        ],
    },
}
DEFAULT_POSITION_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638964424515,
                    's': 'BTCUSDT',
                    'p': '-2214.54000000',
                    'P': '-4.311',
                    'w': '46897.67609538',
                    'x': '51373.17000000',
                    'c': '49155.42000000',
                    'Q': '0.01000000',
                    'b': '49152.96000000',
                    'B': '0.01017300',
                    'a': '49152.97000000',
                    'A': '0.01017300',
                    'o': '51369.96000000',
                    'h': '120000.00000000',
                    'l': '9782.00000000',
                    'v': '1038.52459100',
                    'q': '48704389.88580066',
                    'O': 1638878022537,
                    'C': 1638964422537,
                    'F': 381050,
                    'L': 466268,
                    'n': 85219,
                }
            ],
        }
    ],
    OrderSchema.futures: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639058196458,
                    'E': 1639058196460,
                    'a': {
                        'B': [
                            {
                                'a': 'USDT',
                                'wb': '9999.96949206',
                                'cw': '9950.66684270',
                                'bc': '0',
                            }
                        ],
                        'P': [
                            {
                                's': 'BTCUSDT',
                                'pa': '0.001',
                                'ep': '49294.07000',
                                'cr': '-3973.10941998',
                                'up': '0.00564300',
                                'mt': 'isolated',
                                'iw': '49.30264936',
                                'ps': 'BOTH',
                                'ma': 'USDT',
                            }
                        ],
                        'm': 'ORDER',
                    },
                }
            ],
        }
    ],
    OrderSchema.futures_coin: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639058394216,
                    'E': 1639058394219,
                    'i': 'SgsRoCSgAusR',
                    'a': {
                        'B': [
                            {
                                'a': 'BTC',
                                'wb': '9.99965786',
                                'cw': '9.99965786',
                                'bc': '0',
                            },
                            {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                        ],
                        'P': [
                            {
                                's': 'BTCUSD_PERP',
                                'pa': '1',
                                'ep': '49383.5',
                                'cr': '-0.00018150',
                                'up': '0.00000003',
                                'mt': 'cross',
                                'iw': '0',
                                'ps': 'BOTH',
                                'ma': 'BTC',
                            }
                        ],
                        'm': 'ORDER',
                    },
                }
            ],
        }
    ],
}
DEFAULT_POSITION_GET_DATA_RESULT = {
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
