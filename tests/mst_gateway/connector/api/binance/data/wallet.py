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
DEFAULT_WALLET_DETAIL_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'wallet',
                'sch': 'exchange',
                'act': 'update',
                'd': [
                    {
                        'bls': [
                            {
                                'cur': 'USDT',
                                'bl': 10824.22542493,
                                'upnl': 0.0,
                                'mbl': 10824.22542493,
                                'mm': 49.2,
                                'im': None,
                                'am': 10775.02542493,
                                't': 'trade',
                            }
                        ]
                    }
                ],
            }
        }
    ],
    OrderSchema.futures: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'wallet',
                'sch': 'futures',
                'act': 'update',
                'd': [
                    {
                        'bls': [
                            {
                                'cur': 'USDT',
                                'bl': 9999.96949206,
                                'wbl': 10000.96638768,
                                'bor': 0.0,
                                'ist': 0.0,
                                'upnl': 0.005643,
                                'mbl': 9999.97513506,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 9999.97513506,
                                't': 'trade',
                            }
                        ]
                    }
                ],
            }
        }
    ],
    OrderSchema.futures_coin: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'wallet',
                'sch': 'futures_coin',
                'act': 'update',
                'd': [
                    {
                        'bls': [
                            {
                                'cur': 'BTC',
                                'bl': 9.99965786,
                                'wbl': 9.99951235,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 3e-08,
                                'mbl': 9.99965789,
                                'mm': 8.25e-06,
                                'im': 0.00010314,
                                'am': 9.99964964,
                                't': 'trade',
                            }
                        ]
                    }
                ]
            }
        },
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
                'd': [
                    {
                        'tbl': {'btc': 31.3441251, 'usd': 1527615.17727093},
                        'bls': [
                            {
                                'cur': 'BTC',
                                'bl': 0.991,
                                'upnl': 0.0,
                                'mbl': 0.991,
                                'mm': 0.0,
                                'im': None,
                                'am': 0.991,
                                't': 'trade',
                            },
                            {
                                'cur': 'USDT',
                                'bl': 10824.22542493,
                                'upnl': 0.0,
                                'mbl': 10824.22542493,
                                'mm': 49.2,
                                'im': None,
                                'am': 10775.02542493,
                                't': 'trade',
                            },
                            {
                                'cur': 'BNB',
                                'bl': 1000.0,
                                'wbl': 1000.0,
                                'upnl': 0.0,
                                'mbl': 1000.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 1000.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'BUSD',
                                'bl': 10000.0,
                                'wbl': 10000.0,
                                'upnl': 0.0,
                                'mbl': 10000.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 10000.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'ETH',
                                'bl': 100.0,
                                'wbl': 100.0,
                                'upnl': 0.0,
                                'mbl': 100.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 100.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'LTC',
                                'bl': 500.0,
                                'wbl': 500.0,
                                'upnl': 0.0,
                                'mbl': 500.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 500.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'TRX',
                                'bl': 500000.0,
                                'wbl': 500000.0,
                                'upnl': 0.0,
                                'mbl': 500000.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 500000.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'XRP',
                                'bl': 50000.0,
                                'wbl': 50000.0,
                                'upnl': 0.0,
                                'mbl': 50000.0,
                                'mm': 0.0,
                                'im': None,
                                'am': 50000.0,
                                't': 'trade',
                            },
                        ],
                    }
                ],
            }
        }
    ],
    OrderSchema.futures: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'wallet',
                'sch': 'futures',
                'act': 'update',
                'd': [
                    {
                        'tre': True,
                        'tbl': {'btc': 0.20512901, 'usd': 9999.96949206},
                        'tupnl': {'btc': 1.2e-07, 'usd': 0.005643},
                        'tmbl': {'btc': 0.20512913, 'usd': 9999.97513506},
                        'tbor': {'btc': 0.0, 'usd': 0.0},
                        'tist': {'btc': 0.0, 'usd': 0.0},
                        'tim': 0.0,
                        'tmm': 0.0,
                        'toip': 0.0,
                        'tpim': 0.0,
                        'bls': [
                            {
                                'cur': 'USDT',
                                'bl': 9999.96949206,
                                'wbl': 10000.96638768,
                                'bor': 0.0,
                                'ist': 0.0,
                                'upnl': 0.005643,
                                'mbl': 9999.97513506,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 9999.97513506,
                                't': 'trade',
                            },
                            {
                                'cur': 'BNB',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0.0,
                                'ist': 0.0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'BUSD',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0.0,
                                'ist': 0.0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                        ],
                    }
                ],
            }
        }
    ],
    OrderSchema.futures_coin: [
        {
            'wallet': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'wallet',
                'sch': 'futures_coin',
                'act': 'update',
                'd': [
                    {
                        'tre': True,
                        'tbl': {'btc': 12.8698925, 'usd': 627748.31160829},
                        'tupnl': {'btc': 3e-08, 'usd': 0.00146329},
                        'tmbl': {'btc': 12.86989253, 'usd': 627748.31307159},
                        'tbor': {'btc': 0.0, 'usd': 0.0},
                        'tist': {'btc': 0.0, 'usd': 0.0},
                        'bls': [
                            {
                                'cur': 'BTC',
                                'bl': 9.99965786,
                                'wbl': 9.99951235,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 3e-08,
                                'mbl': 9.99965789,
                                'mm': 8.25e-06,
                                'im': 0.00010314,
                                'am': 9.99964964,
                                't': 'trade',
                            },
                            {
                                'cur': 'ADA',
                                'bl': 100000.0,
                                'wbl': 100000.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': None,
                                'mbl': 100000.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 100000.0,
                                't': 'hold',
                            },
                            {
                                'cur': 'LINK',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'DOGE',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'ETH',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'BNB',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'TRX',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'DOT',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'EOS',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'UNI',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'LTC',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'THETA',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'BCH',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'XRP',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'XLM',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'ETC',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'FIL',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'EGLD',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'SOL',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'LUNA',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'FTM',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'SAND',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'MANA',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'AVAX',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'GALA',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                            {
                                'cur': 'MATIC',
                                'bl': 0.0,
                                'wbl': 0.0,
                                'bor': 0,
                                'ist': 0,
                                'upnl': 0.0,
                                'mbl': 0.0,
                                'mm': 0.0,
                                'im': 0.0,
                                'am': 0.0,
                                't': 'trade',
                            },
                        ],
                    }
                ],
            }
        }
    ],
}
