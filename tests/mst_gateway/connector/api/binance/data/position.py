from mst_gateway.connector.api.types import OrderSchema, LeverageType, PositionSide

DEFAULT_POSITIONS_STATE = {
    OrderSchema.margin: {
        'btcusdt': {
            PositionSide.both: {'action': 'update', 'cross_wallet_balance': 7730.40641563, 'entry_price': 23442.0,
                                'isolated_wallet_balance': 0.0, 'leverage': 10.0, 'leverage_type': LeverageType.cross,
                                'mark_price': 24747.0, 'side': 1, 'position_side': PositionSide.both,
                                'symbol': 'btcusdt', 'volume': 0.1, 'contact_size': None}
        },
        'xrpusdt': {
            PositionSide.both: {'action': 'update', 'cross_wallet_balance': 7730.40641563, 'entry_price': 0.38,
                                'isolated_wallet_balance': 0.0, 'leverage': 25.0, 'leverage_type': LeverageType.cross,
                                'mark_price': 0.37, 'side': 0, 'position_side': PositionSide.both,
                                'symbol': 'ethusdt', 'volume': 27, 'contact_size': None}
        },
        'ltcusdt': {
            PositionSide.both: {'action': 'update', 'cross_wallet_balance': 7730.40641563, 'entry_price': 63.0,
                                'isolated_wallet_balance': 0.0, 'leverage': 20.0, 'leverage_type': LeverageType.cross,
                                'mark_price': 63.0, 'side': 1, 'position_side': PositionSide.both,
                                'symbol': 'ltcusdt', 'volume': 2, 'contact_size': None}
        }
    },
    OrderSchema.margin_coin: {
        'btcusd_perp': {
            PositionSide.both: {'symbol': 'btcusd_perp', 'volume': 1.0, 'side': 0, 'position_side': PositionSide.both,
                                'entry_price': 23994.67406882, 'mark_price': 24398.08989533539,
                                'leverage_type': LeverageType.cross, 'leverage': 3.0,
                                'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 10.00439704,
                                'action': 'update', 'contract_size': 100}
        },
        'xrpusd_perp': {
            PositionSide.both: {'symbol': 'xrpusd_perp', 'volume': 40.0, 'side': 1, 'position_side': PositionSide.both,
                                'entry_price': 0.37, 'mark_price': 0.37,  'leverage_type': LeverageType.cross,
                                'leverage': 1.0, 'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 10.00439704,
                                'action': 'update', 'contract_size': 10}
        },
        'ltcusd_perp': {
            PositionSide.both: {'action': 'update', 'cross_wallet_balance': 10.00439704, 'entry_price': 71.0,
                                'isolated_wallet_balance': 0.0, 'leverage': 10.0, 'leverage_type': LeverageType.cross,
                                'mark_price': 70.0, 'side': 1, 'position_side': PositionSide.both,
                                'symbol': 'ltcusd_perp', 'volume': 3, 'contact_size': 10}
        }
    }
}

HEDGE_MODE_POSITIONS_STATE = {
    OrderSchema.margin: {
        'ltcusdt': {
            PositionSide.long: {'symbol': 'ltcusdt', 'volume': 1.0, 'side': 0, 'position_side': PositionSide.long,
                                'entry_price': 61.07, 'mark_price': 61.07689862, 'leverage_type': LeverageType.cross,
                                'leverage': 20.0, 'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 2982.33359418,
                                'action': 'update', 'contract_size': None},
            PositionSide.short: {'symbol': 'ltcusdt', 'volume': -2.0, 'side': 1, 'position_side': PositionSide.short,
                                 'entry_price': 61.18, 'mark_price': 61.07689862, 'leverage_type': LeverageType.cross,
                                 'leverage': 20.0, 'isolated_wallet_balance': 0.0,
                                 'cross_wallet_balance': 2982.33359418, 'action': 'update', 'contract_size': None}
        },
        'btcusdt': {
            PositionSide.long: {'symbol': 'btcusdt', 'volume': 0.002, 'side': 0, 'position_side': PositionSide.long,
                                'entry_price': 24057.75, 'mark_price': 24015.63094,
                                'leverage_type': LeverageType.cross, 'leverage': 10.0,
                                'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 2982.33359418,
                                'action': 'update', 'contract_size': None},
            PositionSide.short: {'symbol': 'btcusdt', 'volume': -0.002, 'side': 1, 'position_side': PositionSide.short,
                                 'entry_price': 24064.7, 'mark_price': 24015.63094, 'leverage_type': LeverageType.cross,
                                 'leverage': 10.0, 'isolated_wallet_balance': 0.0,
                                 'cross_wallet_balance': 2982.33359418, 'action': 'update', 'contract_size': None}
        },
        'xrpusdt': {
            PositionSide.long: {'symbol': 'xrpusdt', 'volume': 54.0, 'side': 0, 'position_side': PositionSide.long,
                                'entry_price': 0.37755, 'mark_price': 0.36902149, 'leverage_type': LeverageType.cross,
                                'leverage': 20.0, 'isolated_wallet_balance': 0.0,
                                'cross_wallet_balance': 2982.33359418, 'action': 'update', 'contract_size': None},
            PositionSide.short: {'symbol': 'xrpusdt', 'volume': -100.0, 'side': 1, 'position_side': PositionSide.short,
                                 'entry_price': 0.3747194, 'mark_price': 0.36902148999999995,
                                 'leverage_type': LeverageType.cross, 'leverage': 20.0,
                                 'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 2982.33359418,
                                 'action': 'update', 'contract_size': None}
        }
    },
    OrderSchema.margin_coin: {
        'btcusd_perp': {
            PositionSide.long: {'symbol': 'btcusd_perp', 'volume': 1.0, 'side': 0, 'position_side': PositionSide.long,
                                'entry_price': 24047.39999982, 'mark_price': 24059.955172062208,
                                'leverage_type': LeverageType.cross, 'leverage': 12.0, 'isolated_wallet_balance': 0.0,
                                'cross_wallet_balance': 10.00473372, 'action': 'update', 'contract_size': 100},
            PositionSide.short: {'symbol': 'btcusd_perp', 'volume': -2.0, 'side': 1,
                                 'position_side': PositionSide.short, 'entry_price': 24054.80000011,
                                 'mark_price': 24059.9798842469, 'leverage_type': LeverageType.cross, 'leverage': 12.0,
                                 'isolated_wallet_balance': 0.0, 'cross_wallet_balance': 10.00473372,
                                 'action': 'update', 'contract_size': 100}
        }
    }
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
                    'mt': LeverageType.cross,
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
                    'mt': LeverageType.cross,
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
                            'mt': LeverageType.cross,
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
                            'mt': LeverageType.cross,
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
                                'mt': LeverageType.cross,
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
                                'mt': LeverageType.cross,
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
                        'ps': PositionSide.both,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 46978.37598999999,
                        'upnl': 0.010815989999995508,
                        'lvrp': LeverageType.cross,
                        'lp': None,
                        'lvr': 10.0,
                        'act': 'create',
                        'ss': 'btcusdt',
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
                        'ps': PositionSide.both,
                        'vl': 1.0,
                        'ep': 46978.5,
                        'mp': 46978.27930309058,
                        'upnl': -1.0000000000021927e-08,
                        'lvrp': LeverageType.cross,
                        'lvr': 3.0,
                        'lp': None,
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
                                'mt': LeverageType.cross,
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
                    'ps': PositionSide.both
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
                    'ps': PositionSide.both
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
                                'mt': LeverageType.cross,
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
                                'mt': LeverageType.cross,
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
                    'leverage_type': LeverageType.cross,
                    'unrealised_pnl': -8e-08,
                    'liquidation_price': 10.04319695,
                    'position_side': PositionSide.both
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
                    'ps': PositionSide.both
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
                                'mt': LeverageType.cross,
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
                        'ps': PositionSide.both,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 46978.37598999999,
                        'upnl': 0.010815989999995508,
                        'lvrp': LeverageType.cross,
                        'lp': None,
                        'lvr': 10.0,
                        'act': 'create',
                        'ss': 'btcusdt',
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
                        'ps': PositionSide.both,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 47051.32491159,
                        'upnl': 0.08376491159000579,
                        'lvrp': LeverageType.cross,
                        'lvr': 10.0,
                        'lp': None,
                        'act': 'update',
                        'ss': 'btcusdt',
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
                        'ps': PositionSide.both,
                        'vl': 0.001,
                        'ep': 46967.56,
                        'mp': 47051.32491159,
                        'upnl': 0.08376491159000579,
                        'lvrp': LeverageType.cross,
                        'lvr': 3.0,
                        'lp': None,
                        'act': 'update',
                        'ss': 'btcusdt',
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
                        'ps': PositionSide.both,
                        'vl': 0.0,
                        'ep': 0.0,
                        'mp': None,
                        'upnl': None,
                        'lvrp': LeverageType.cross,
                        'lvr': 3.0,
                        'lp': None,
                        'act': 'delete',
                        'ss': 'btcusdt',
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
                        'ps': PositionSide.both,
                        'vl': 1.0,
                        'ep': 46978.5,
                        'mp': 46978.27930309058,
                        'upnl': -1.0000000000021927e-08,
                        'lvrp': LeverageType.cross,
                        'lp': None,
                        'lvr': 3.0,
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
                        'ps': PositionSide.both,
                        'vl': 1.0,
                        'ep': 46978.49999962,
                        'mp': 46976.6,
                        'upnl': -8e-08,
                        'lvrp': LeverageType.cross,
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
                        'ps': PositionSide.both,
                        'vl': 1.0,
                        'ep': 46978.49999962,
                        'mp': 47051.32491159,
                        'upnl': 3.2946475743515633e-06,
                        'lvrp': LeverageType.cross,
                        'lvr': 3.0,
                        'lp': None,
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
                        'ps': PositionSide.both,
                        'vl': 0.0,
                        'ep': 0.0,
                        'mp': None,
                        'upnl': None,
                        'lvrp': LeverageType.cross,
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
