from mst_gateway.connector.api.types import OrderSchema, LeverageType

DEFAULT_POSITIONS_STATE = {
    OrderSchema.margin: {
        'btcusdt': {
            'action': 'update',
            'cross_wallet_balance': 99760.41099324,
            'entry_price': 57000.0,
            'isolated_wallet_balance': 100000.0,
            'leverage': 1.0,
            'leverage_type': LeverageType.cross,
            'mark_price': 56900.0,
            'side': 1,
            'symbol': 'btcusdt',
            'volume': 0.001,
        },
    },
    OrderSchema.margin_coin: {
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
    },
}


DEFAULT_POSITION_MESSAGE = {
    OrderSchema.margin: {
        'e': 'ACCOUNT_UPDATE',
        'T': 1639499597056,
        'E': 1639499597059,
        'a': {
            'B': [
                {'a': 'USDT', 'wb': '10000.39627811', 'cw': '10000.39627811', 'bc': '0'}
            ],
            'P': [
                {
                    's': 'BTCUSDT',
                    'pa': '0.001',
                    'ep': '46967.56000',
                    'cr': '-3973.22553998',
                    'up': '0.01081599',
                    'mt': 'cross',
                    'iw': '0',
                    'ps': 'BOTH',
                    'ma': 'USDT',
                }
            ],
            'm': 'ORDER',
        },
    },
    OrderSchema.margin_coin: {
        'e': 'ACCOUNT_UPDATE',
        'T': 1639500263840,
        'E': 1639500263852,
        'i': 'SgsRoCSgAusR',
        'a': {
            'B': [
                {'a': 'BTC', 'wb': '9.99964515', 'cw': '9.99964515', 'bc': '0'},
                {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
            ],
            'P': [
                {
                    's': 'BTCUSD_PERP',
                    'pa': '1',
                    'ep': '46978.5',
                    'cr': '-0.00018340',
                    'up': '-0.00000001',
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
    OrderSchema.margin: {
        'table': 'ACCOUNT_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ACCOUNT_UPDATE',
                'T': 1639499597056,
                'E': 1639499597059,
                'a': {
                    'B': [
                        {
                            'a': 'USDT',
                            'wb': '10000.39627811',
                            'cw': '10000.39627811',
                            'bc': '0',
                        }
                    ],
                    'P': [
                        {
                            's': 'BTCUSDT',
                            'pa': '0.001',
                            'ep': '46967.56000',
                            'cr': '-3973.22553998',
                            'up': '0.01081599',
                            'mt': 'cross',
                            'iw': '0',
                            'ps': 'BOTH',
                            'ma': 'USDT',
                        }
                    ],
                    'm': 'ORDER',
                },
            }
        ],
    },
    OrderSchema.margin_coin: {
        'table': 'ACCOUNT_UPDATE',
        'action': 'update',
        'data': [
            {
                'e': 'ACCOUNT_UPDATE',
                'T': 1639500263840,
                'E': 1639500263852,
                'i': 'SgsRoCSgAusR',
                'a': {
                    'B': [
                        {'a': 'BTC', 'wb': '9.99964515', 'cw': '9.99964515', 'bc': '0'},
                        {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                    ],
                    'P': [
                        {
                            's': 'BTCUSD_PERP',
                            'pa': '1',
                            'ep': '46978.5',
                            'cr': '-0.00018340',
                            'up': '-0.00000001',
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
    OrderSchema.margin: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639499597056,
                    'E': 1639499597059,
                    'a': {
                        'B': [
                            {
                                'a': 'USDT',
                                'wb': '10000.39627811',
                                'cw': '10000.39627811',
                                'bc': '0',
                            }
                        ],
                        'P': [
                            {
                                's': 'BTCUSDT',
                                'pa': '0.001',
                                'ep': '46967.56000',
                                'cr': '-3973.22553998',
                                'up': '0.01081599',
                                'mt': 'cross',
                                'iw': '0',
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
    OrderSchema.margin_coin: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639500263840,
                    'E': 1639500263852,
                    'i': 'SgsRoCSgAusR',
                    'a': {
                        'B': [
                            {
                                'a': 'BTC',
                                'wb': '9.99964515',
                                'cw': '9.99964515',
                                'bc': '0',
                            },
                            {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                        ],
                        'P': [
                            {
                                's': 'BTCUSD_PERP',
                                'pa': '1',
                                'ep': '46978.5',
                                'cr': '-0.00018340',
                                'up': '-0.00000001',
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
    OrderSchema.margin: [
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:33:17.059000',
                        's': 'btcusdt',
                        'sd': 0,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 46978.37598999999,
                        'upnl': 0.010815989999995508,
                        'lvrp': 'cross',
                        'lvr': 1.0,
                        'lp': None,
                        'act': 'create',
                        'ss': 'btcusd',
                    }
                ],
            }
        }
    ],
    OrderSchema.margin_coin: [
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:44:23.852000',
                        's': 'btcusd_perp',
                        'sd': 0,
                        'vl': 1.0,
                        'ep': 46978.5,
                        'mp': 46978.27930309058,
                        'upnl': -1.0000000000021927e-08,
                        'lvrp': 'cross',
                        'lvr': 1.0,
                        'lp': 10.040358419266353,
                        'act': 'create',
                        'ss': 'btcusd',
                    }
                ],
            }
        }
    ],
}
DEFAULT_POSITION_DETAIL_MESSAGES = {
    OrderSchema.margin: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639499597056,
                    'E': 1639499597059,
                    'a': {
                        'B': [
                            {
                                'a': 'USDT',
                                'wb': '10000.39627811',
                                'cw': '10000.39627811',
                                'bc': '0',
                            }
                        ],
                        'P': [
                            {
                                's': 'BTCUSDT',
                                'pa': '0.001',
                                'ep': '46967.56000',
                                'cr': '-3973.22553998',
                                'up': '0.01081599',
                                'mt': 'isolated',
                                'iw': '0',
                                'ps': 'BOTH',
                                'ma': 'USDT',
                            }
                        ],
                        'm': 'ORDER',
                    },
                }
            ],
        },
        {
            'table': 'markPriceUpdate',
            'action': 'update',
            'data': [
                {
                    'e': 'markPriceUpdate',
                    'E': 1639498245000,
                    's': 'BTCUSDT',
                    'p': '47051.32491159',
                    'P': '46854.81160179',
                    'i': '47050.61725278',
                    'r': '0.00010000',
                    'T': 1639526400000,
                }
            ],
        },
        {
            'table': 'ACCOUNT_CONFIG_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_CONFIG_UPDATE',
                    'T': 1639499709845,
                    'E': 1639499709847,
                    'ac': {'s': 'BTCUSDT', 'l': 3},
                }
            ],
        },
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639499713374,
                    'E': 1639499713377,
                    'a': {
                        'B': [
                            {
                                'a': 'USDT',
                                'wb': '10000.44177537',
                                'cw': '10000.44177537',
                                'bc': '0',
                            }
                        ],
                        'P': [
                            {
                                's': 'BTCUSDT',
                                'pa': '0',
                                'ep': '0.00000',
                                'cr': '-3973.16122998',
                                'up': '0',
                                'mt': 'isolated',
                                'iw': '0',
                                'ps': 'BOTH',
                                'ma': 'USDT',
                            }
                        ],
                        'm': 'ORDER',
                    },
                }
            ],
        },
    ],
    OrderSchema.margin_coin: [
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639500263840,
                    'E': 1639500263852,
                    'i': 'SgsRoCSgAusR',
                    'a': {
                        'B': [
                            {
                                'a': 'BTC',
                                'wb': '9.99964515',
                                'cw': '9.99964515',
                                'bc': '0',
                            },
                            {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                        ],
                        'P': [
                            {
                                's': 'BTCUSD_PERP',
                                'pa': '1',
                                'ep': '46978.5',
                                'cr': '-0.00018340',
                                'up': '-0.00000001',
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
        {
            'table': 'position',
            'action': 'update',
            'data': [
                {
                    'E': 1639500273210,
                    'symbol': 'BTCUSD_PERP',
                    'volume': 1.0,
                    'side': 0,
                    'entry_price': 46978.49999962,
                    'mark_price': 46976.6,
                    'leverage': 3.0,
                    'leverage_type': 'cross',
                    'unrealised_pnl': -8e-08,
                    'liquidation_price': 10.04319695,
                }
            ],
        },
        {
            'table': 'markPriceUpdate',
            'action': 'update',
            'data': [
                {
                    'e': 'markPriceUpdate',
                    'E': 1639498245000,
                    's': 'BTCUSD_PERP',
                    'p': '47051.32491159',
                    'P': '46854.81160179',
                    'i': '47050.61725278',
                    'r': '0.00010000',
                    'T': 1639526400000,
                }
            ],
        },
        {
            'table': 'ACCOUNT_UPDATE',
            'action': 'update',
            'data': [
                {
                    'e': 'ACCOUNT_UPDATE',
                    'T': 1639500279316,
                    'E': 1639500279328,
                    'i': 'SgsRoCSgAusR',
                    'a': {
                        'B': [
                            {
                                'a': 'BTC',
                                'wb': '9.99964401',
                                'cw': '9.99964401',
                                'bc': '0',
                            },
                            {'a': 'ADA', 'wb': '100000', 'cw': '100000', 'bc': '0'},
                        ],
                        'P': [
                            {
                                's': 'BTCUSD_PERP',
                                'pa': '0',
                                'ep': '0.0',
                                'cr': '-0.00018348',
                                'up': '0',
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
    ],
}
DEFAULT_POSITION_DETAIL_GET_DATA_RESULT = {
    OrderSchema.margin: [
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:33:17.059000',
                        's': 'btcusdt',
                        'sd': 0,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 46978.37598999999,
                        'upnl': 0.010815989999995508,
                        'lvrp': 'isolated',
                        'lvr': 1.0,
                        'lp': 47156.184738955824,
                        'act': 'create',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:10:45.000000',
                        's': 'btcusdt',
                        'sd': 0,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 47051.32491159,
                        'upnl': 0.08376491159000579,
                        'lvrp': 'isolated',
                        'lvr': 1.0,
                        'lp': 47156.184738955824,
                        'act': 'update',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:35:09.847000',
                        's': 'btcusdt',
                        'sd': 0,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 47051.32491159,
                        'upnl': 0.08376491159000579,
                        'lvrp': 'isolated',
                        'lvr': 3.0,
                        'lp': 47156.184738955824,
                        'act': 'update',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:35:13.377000',
                        's': 'btcusdt',
                        'sd': 0,
                        'vl': 0.0,
                        'ep': 0.0,
                        'mp': None,
                        'upnl': None,
                        'lvrp': 'isolated',
                        'lvr': 3.0,
                        'lp': None,
                        'act': 'delete',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
    ],
    OrderSchema.margin_coin: [
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:44:23.852000',
                        's': 'btcusd_perp',
                        'sd': 0,
                        'vl': 1.0,
                        'ep': 46978.5,
                        'mp': 46978.27930309058,
                        'upnl': -1.0000000000021927e-08,
                        'lvrp': 'cross',
                        'lvr': 1.0,
                        'lp': 10.040358419266353,
                        'act': 'create',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:44:33.210000',
                        's': 'btcusd_perp',
                        'sd': 0,
                        'vl': 1.0,
                        'ep': 46978.49999962,
                        'mp': 46976.6,
                        'upnl': -8e-08,
                        'lvrp': 'cross',
                        'lvr': 3.0,
                        'lp': 10.04319695,
                        'act': 'update',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:10:45.000000',
                        's': 'btcusd_perp',
                        'sd': 0,
                        'vl': 1.0,
                        'ep': 46978.49999962,
                        'mp': 47051.32491159,
                        'upnl': 3.2946475743515633e-06,
                        'lvrp': 'cross',
                        'lvr': 3.0,
                        'lp': 10.040358419266353,
                        'act': 'update',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
        {
            'position': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'position',
                'sch': 'margin_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-14T16:44:39.328000',
                        's': 'btcusd_perp',
                        'sd': 0,
                        'vl': 0.0,
                        'ep': 0.0,
                        'mp': None,
                        'upnl': None,
                        'lvrp': 'cross',
                        'lvr': 3.0,
                        'lp': None,
                        'act': 'delete',
                        'ss': 'btcusd',
                    }
                ],
            }
        },
    ],
}
