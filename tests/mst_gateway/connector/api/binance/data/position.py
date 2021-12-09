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
    OrderSchema.futures: [],
    OrderSchema.futures_coin: [],
}
