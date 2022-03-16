from mst_gateway.connector.api.types import OrderSchema

DEFAULT_WALLET_MESSAGE = {
    OrderSchema.exchange: {
        'e': 'outboundAccountPosition',
        'E': 1639057750403,
        'u': 1639057750402,
        'B': [
            {'a': 'BTC', 'f': '0.99100000', 'l': '0.00000000'},
            {'a': 'USDT', 'f': '10824.22542493', 'l': '49.20000000'},
        ],
    },
    OrderSchema.margin: {
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
    OrderSchema.margin_coin: {
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
DEFAULT_WALLET_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': 'outboundAccountPosition',
        'action': 'update',
        'data': [
            {
                'e': 'outboundAccountPosition',
                'E': 1639057750403,
                'u': 1639057750402,
                'B': [
                    {'a': 'BTC', 'f': '0.99100000', 'l': '0.00000000'},
                    {'a': 'USDT', 'f': '10824.22542493', 'l': '49.20000000'},
                ],
            }
        ],
    },
    OrderSchema.margin: {
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
    OrderSchema.margin_coin: {
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
DEFAULT_WALLET_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': 'outboundAccountPosition',
            'action': 'update',
            'data': [
                {
                    'e': 'outboundAccountPosition',
                    'E': 1639057750403,
                    'u': 1639057750402,
                    'B': [
                        {'a': 'BTC', 'f': '0.99100000', 'l': '0.00000000'},
                        {'a': 'USDT', 'f': '10824.22542493', 'l': '49.20000000'},
                    ],
                }
            ],
        }
    ],
    OrderSchema.margin: [
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
    OrderSchema.margin_coin: [
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
DEFAULT_WALLET_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'wallet',
                'sch': 'exchange',
                'act': 'update',
                'd': {
                    'bls': [
                        {
                            'cur': 'BTC',
                            'bl': 0.991,
                            'wbl': 0.991,
                            'upnl': 0.0,
                            'mbl': 0.991,
                            'mm': 0.0,
                            'im': 0.0,
                            'am': 0.991,
                            't': 'hold'
                        },
                        {
                            'cur': 'USDT',
                            'bl': 10873.42542493,
                            'wbl': 10824.22542493,
                            'upnl': 0.0,
                            'mbl': 10873.42542493,
                            'mm': 0.0,
                            'im': 49.2,
                            'am': 10824.22542493,
                            't': 'hold'
                        }
                    ],
                },
                'ex': None,
            }
        }
    ],
    OrderSchema.margin: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'wallet',
                'sch': OrderSchema.margin,
                'act': 'update',
                'd': {
                    'bls': [
                        {
                            'cur': 'USDT',
                            'bl': 9999.96949206,
                            'wbl': 9999.97513506,
                            'upnl': 0.005643,
                            'mbl': 9999.97513506,
                            'mm': 0.0,
                            'im': 0.0,
                            'am': 9999.97513506,
                            't': 'trade'
                        },
                        {
                            'cur': 'BNB',
                            'bl': 0.0,
                            'wbl': 0.0,
                            'upnl': 0.0,
                            'mbl': 0.0,
                            'mm': 0.0,
                            'im': 0.0,
                            'am': 0.0,
                            't': 'trade'
                        },
                        {
                            'cur': 'BUSD',
                            'bl': 0.0,
                            'wbl': 0.0,
                            'upnl': 0.0,
                            'mbl': 0.0,
                            'mm': 0.0,
                            'im': 0.0,
                            'am': 0.0,
                            't': 'trade'
                        },
                    ],
                },
                'ex': {
                    'bls': [
                        {
                            'cur': 'USDT',
                            'bor': 0.0,
                            'ist': 0.0
                        },
                        {
                            'cur': 'BNB',
                            'bor': 0.0,
                            'ist': 0.0
                        },
                        {
                            'cur': 'BUSD',
                            'bor': 0.0,
                            'ist': 0.0
                        },
                    ],
                    'tre': True
                }
            }
        }
    ],
    OrderSchema.margin_coin: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_margin',
                'tb': 'wallet',
                'sch': 'margin_coin',
                'act': 'update',
                'd': {
                    'bls': [
                        {
                            'cur': 'BTC',
                            'bl': 9.99965786,
                            'wbl': 9.99955475,
                            'upnl': 3e-08,
                            'mbl': 9.99965789,
                            'mm': 8.25e-06,
                            'im': 0.00010314,
                            'am': 9.99955475,
                            't': 'trade'
                        },
                        {
                            'cur': 'ADA',
                            'bl': 100000.0,
                            'wbl': 100000.0,
                            'upnl': 0.0,
                            'mbl': 100000.0,
                            'mm': 0.0,
                            'im': 0.0,
                            'am': 100000.0,
                            't': 'hold'
                        }
                    ],
                },
                'ex': {
                    'tre': True
                }
            }
        }
    ],
}

DEFAULT_WALLET_STATE = {
    OrderSchema.exchange: {
        'tbl': {'btc': 0.20512901, 'usd': 9999.96949206},
        'tupnl': {'btc': 0.0, 'usd': 0.0},
        'tmbl': {'btc': 0.0, 'usd': 0.0},
        'bls': {
            'btc': {
                'cur': 'BTC',
                'bl': 0.991,
                'wbl': 0.991,
                'upnl': 0.0,
                'mbl': 0.991,
                'mm': 0.0,
                'im': 0.0,
                'am': 0.991,
                't': 'hold'
            },
            'usdt': {
                'cur': 'USDT',
                'bl': 10873.42542493,
                'wbl': 10824.22542493,
                'upnl': 0.0,
                'mbl': 10873.42542493,
                'mm': 0.0,
                'im': 49.2,
                'am': 10824.22542493,
                't': 'hold'
            }
        },
        'ex': None
    },
    OrderSchema.margin: {
        'bls': {
            'usdt': {
                'cur': 'USDT',
                'bl': 9999.96949206,
                'wbl': 9999.97513506,
                'upnl': 0.0,
                'mbl': 9999.97513506,
                'mm': 0.0,
                'im': 0.0,
                'am': 9999.97513506,
                't': 'trade'
            },
            'bnb': {
                'cur': 'BNB',
                'bl': 0.0,
                'wbl': 0.0,
                'upnl': 0.0,
                'mbl': 0.0,
                'mm': 0.0,
                'im': 0.0,
                'am': 0.0,
                't': 'trade'
            },
            'busd': {
                'cur': 'BUSD',
                'bl': 0.0,
                'wbl': 0.0,
                'upnl': 0.0,
                'mbl': 0.0,
                'mm': 0.0,
                'im': 0.0,
                'am': 0.0,
                't': 'trade'
            }
        },
        'ex': {
            'bls': {
                'usdt': {
                    'cur': 'USDT',
                    'bor': 0.0,
                    'ist': 0.0
                },
                'bnb': {
                    'cur': 'BNB',
                    'bor': 0.0,
                    'ist': 0.0
                },
                'busd': {
                    'cur': 'BUSD',
                    'bor': 0.0,
                    'ist': 0.0
                }
            },
            'tre': True
        }
    },
    OrderSchema.margin_coin: {
        'bls': {
            'btc': {
                'cur': 'BTC',
                'bl': 9.99965786,
                'wbl': 9.99951235,
                'upnl': 3e-08,
                'mbl': 9.99965789,
                'mm': 8.25e-06,
                'im': 0.00010314,
                'am': 9.99964964,
                't': 'trade'
            },
            'ada': {
                'cur': 'ADA',
                'bl': 100000.0,
                'wbl': 100000.0,
                'upnl': 0.0,
                'mbl': 100000.0,
                'mm': 0.0,
                'im': 0.0,
                'am': 100000.0,
                't': 'hold'
            }
        },
        'ex': {
            'tre': True
        }
    }
}
