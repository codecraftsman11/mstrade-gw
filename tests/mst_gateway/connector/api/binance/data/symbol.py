from mst_gateway.connector.api.types import OrderSchema

DEFAULT_LEVERAGE_BRACKETS = {
    OrderSchema.futures: [
        {'bracket': 1, 'initialLeverage': 125, 'notionalCap': 50000, 'notionalFloor': 0,
         'maintMarginRatio': 0.004, 'cum': 0.0},
        {'bracket': 2, 'initialLeverage': 100, 'notionalCap': 250000, 'notionalFloor': 50000,
         'maintMarginRatio': 0.005, 'cum': 50.0},
        {'bracket': 3, 'initialLeverage': 50, 'notionalCap': 1000000, 'notionalFloor': 250000,
         'maintMarginRatio': 0.01, 'cum': 1300.0},
        {'bracket': 4, 'initialLeverage': 20, 'notionalCap': 10000000, 'notionalFloor': 1000000,
         'maintMarginRatio': 0.025, 'cum': 16300.0},
        {'bracket': 5, 'initialLeverage': 10, 'notionalCap': 20000000, 'notionalFloor': 10000000,
         'maintMarginRatio': 0.05, 'cum': 266300.0},
        {'bracket': 6, 'initialLeverage': 5, 'notionalCap': 50000000, 'notionalFloor': 20000000,
         'maintMarginRatio': 0.1, 'cum': 1266300.0},
        {'bracket': 7, 'initialLeverage': 4, 'notionalCap': 100000000, 'notionalFloor': 50000000,
         'maintMarginRatio': 0.125, 'cum': 2516300.0},
        {'bracket': 8, 'initialLeverage': 3, 'notionalCap': 200000000, 'notionalFloor': 100000000,
         'maintMarginRatio': 0.15, 'cum': 5016300.0},
        {'bracket': 9, 'initialLeverage': 2, 'notionalCap': 300000000, 'notionalFloor': 200000000,
         'maintMarginRatio': 0.25, 'cum': 25016300.0},
        {'bracket': 10, 'initialLeverage': 1, 'notionalCap': 9223372036854775807, 'notionalFloor': 300000000,
         'maintMarginRatio': 0.5, 'cum': 100016300.0}],
    OrderSchema.futures_coin: [
        {'bracket': 1, 'initialLeverage': 125, 'qtyCap': 5, 'qtyFloor': 0, 'maintMarginRatio': 0.004, 'cum': 0.0},
        {'bracket': 2, 'initialLeverage': 100, 'qtyCap': 10, 'qtyFloor': 5, 'maintMarginRatio': 0.005, 'cum': 0.005},
        {'bracket': 3, 'initialLeverage': 50, 'qtyCap': 20, 'qtyFloor': 10, 'maintMarginRatio': 0.01, 'cum': 0.055},
        {'bracket': 4, 'initialLeverage': 20, 'qtyCap': 50, 'qtyFloor': 20, 'maintMarginRatio': 0.025, 'cum': 0.355},
        {'bracket': 5, 'initialLeverage': 10, 'qtyCap': 100, 'qtyFloor': 50, 'maintMarginRatio': 0.05, 'cum': 1.605},
        {'bracket': 6, 'initialLeverage': 5, 'qtyCap': 200, 'qtyFloor': 100, 'maintMarginRatio': 0.1, 'cum': 6.605},
        {'bracket': 7, 'initialLeverage': 4, 'qtyCap': 400, 'qtyFloor': 200, 'maintMarginRatio': 0.125, 'cum': 11.605},
        {'bracket': 8, 'initialLeverage': 3, 'qtyCap': 1000, 'qtyFloor': 400, 'maintMarginRatio': 0.15, 'cum': 21.605},
        {'bracket': 9, 'initialLeverage': 2, 'qtyCap': 1500, 'qtyFloor': 1000, 'maintMarginRatio': 0.25,
         'cum': 121.605},
        {'bracket': 10, 'initialLeverage': 1, 'qtyCap': 9223372036854775807, 'qtyFloor': 1500, 'maintMarginRatio': 0.5,
         'cum': 496.605}]
}


DEFAULT_SYMBOL_DETAIL_MESSAGE = {
    OrderSchema.exchange: {
        'e': '24hrTicker',
        'E': 1638958912283,
        's': 'BTCUSDT',
        'p': '-913.00000000',
        'P': '-1.785',
        'w': '46916.15896045',
        'x': '51161.90000000',
        'c': '50244.80000000',
        'Q': '0.00995200',
        'b': '50245.94000000',
        'B': '0.00995200',
        'a': '50245.97000000',
        'A': '0.00995200',
        'o': '51157.80000000',
        'h': '120000.00000000',
        'l': '9782.00000000',
        'v': '1024.21748400',
        'q': '48052350.28941604',
        'O': 1638872511231,
        'C': 1638958911231,
        'F': 376355,
        'L': 459561,
        'n': 83207,
    },
    OrderSchema.futures: {
        'e': '24hrTicker',
        'E': 1638964455555,
        's': 'BTCUSDT',
        'p': '-2190.81',
        'P': '-4.265',
        'w': '50649.55',
        'c': '49174.26',
        'Q': '0.010',
        'o': '51365.07',
        'h': '53900.00',
        'l': '48841.07',
        'v': '1941684.425',
        'q': '98345450984.67',
        'O': 1638878040000,
        'C': 1638964455553,
        'F': 216977693,
        'L': 217094660,
        'n': 116540,
    },
    OrderSchema.futures_coin: {
        'e': '24hrTicker',
        'E': 1638965331103,
        's': 'BTCUSD_PERP',
        'ps': 'BTCUSD',
        'p': '-2120.6',
        'P': '-4.131',
        'w': '50667.09303835',
        'c': '49214.9',
        'Q': '3',
        'o': '51335.5',
        'h': '55487.2',
        'l': '47014.3',
        'v': '342444',
        'q': '675.87062818',
        'O': 1638878880000,
        'C': 1638965331092,
        'F': 50016490,
        'L': 50097296,
        'n': 80807,
    },
}
DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638958912283,
                's': 'BTCUSDT',
                'p': '-913.00000000',
                'P': '-1.785',
                'w': '46916.15896045',
                'x': '51161.90000000',
                'c': '50244.80000000',
                'Q': '0.00995200',
                'b': '50245.94000000',
                'B': '0.00995200',
                'a': '50245.97000000',
                'A': '0.00995200',
                'o': '51157.80000000',
                'h': '120000.00000000',
                'l': '9782.00000000',
                'v': '1024.21748400',
                'q': '48052350.28941604',
                'O': 1638872511231,
                'C': 1638958911231,
                'F': 376355,
                'L': 459561,
                'n': 83207,
            }
        ],
    },
    OrderSchema.futures: {
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638964455555,
                's': 'BTCUSDT',
                'p': '-2190.81',
                'P': '-4.265',
                'w': '50649.55',
                'c': '49174.26',
                'Q': '0.010',
                'o': '51365.07',
                'h': '53900.00',
                'l': '48841.07',
                'v': '1941684.425',
                'q': '98345450984.67',
                'O': 1638878040000,
                'C': 1638964455553,
                'F': 216977693,
                'L': 217094660,
                'n': 116540,
            }
        ],
    },
    OrderSchema.futures_coin: {
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638965331103,
                's': 'BTCUSD_PERP',
                'ps': 'BTCUSD',
                'p': '-2120.6',
                'P': '-4.131',
                'w': '50667.09303835',
                'c': '49214.9',
                'Q': '3',
                'o': '51335.5',
                'h': '55487.2',
                'l': '47014.3',
                'v': '342444',
                'q': '675.87062818',
                'O': 1638878880000,
                'C': 1638965331092,
                'F': 50016490,
                'L': 50097296,
                'n': 80807,
            }
        ],
    },
}
DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [
        {
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638958912283,
                    's': 'BTCUSDT',
                    'p': '-913.00000000',
                    'P': '-1.785',
                    'w': '46916.15896045',
                    'x': '51161.90000000',
                    'c': '50244.80000000',
                    'Q': '0.00995200',
                    'b': '50245.94000000',
                    'B': '0.00995200',
                    'a': '50245.97000000',
                    'A': '0.00995200',
                    'o': '51157.80000000',
                    'h': '120000.00000000',
                    'l': '9782.00000000',
                    'v': '1024.21748400',
                    'q': '48052350.28941604',
                    'O': 1638872511231,
                    'C': 1638958911231,
                    'F': 376355,
                    'L': 459561,
                    'n': 83207,
                }
            ],
        }
    ],
    OrderSchema.futures: [
        {
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638964455555,
                    's': 'BTCUSDT',
                    'p': '-2190.81',
                    'P': '-4.265',
                    'w': '50649.55',
                    'c': '49174.26',
                    'Q': '0.010',
                    'o': '51365.07',
                    'h': '53900.00',
                    'l': '48841.07',
                    'v': '1941684.425',
                    'q': '98345450984.67',
                    'O': 1638878040000,
                    'C': 1638964455553,
                    'F': 216977693,
                    'L': 217094660,
                    'n': 116540,
                }
            ],
        }
    ],
    OrderSchema.futures_coin: [
        {
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638965331103,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'p': '-2120.6',
                    'P': '-4.131',
                    'w': '50667.09303835',
                    'c': '49214.9',
                    'Q': '3',
                    'o': '51335.5',
                    'h': '55487.2',
                    'l': '47014.3',
                    'v': '342444',
                    'q': '675.87062818',
                    'O': 1638878880000,
                    'C': 1638965331092,
                    'F': 50016490,
                    'L': 50097296,
                    'n': 80807,
                }
            ],
        }
    ],
}
DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'symbol',
                'sch': 'exchange',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T10:21:52.283000',
                        's': 'BTCUSDT',
                        'p': 50244.8,
                        'p24': 51157.8,
                        'dt': -1.78,
                        'fp': 50244.8,
                        'bip': 50245.94,
                        'asp': 50245.97,
                        're': False,
                        'v24': 1024.217484,
                        'mp': 50244.8,
                        'hip': 120000.0,
                        'lop': 9782.0,
                        'exp': None,
                        'expd': None,
                        'pa': ['BTC', 'USDT'],
                        'tck': 0.01,
                        'vt': 1e-06,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.271836',
                        'mlvr': None,
                    }
                ],
            }
        }
    ],
    OrderSchema.futures: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'symbol',
                'sch': 'futures',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T11:54:15.555000',
                        's': 'BTCUSDT',
                        'p': 49174.26,
                        'p24': 51365.07,
                        'dt': -4.27,
                        'fp': 49174.26,
                        'bip': 0.0,
                        'asp': 0.0,
                        're': False,
                        'v24': 1941684.425,
                        'mp': 0.0,
                        'hip': 53900.0,
                        'lop': 48841.07,
                        'exp': 'None',
                        'expd': 'None',
                        'pa': ['BTC', 'USDT'],
                        'tck': 0.01,
                        'vt': 0.001,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.272746',
                        'mlvr': 125.0,
                    }
                ],
            }
        }
    ],
    OrderSchema.futures_coin: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'symbol',
                'sch': 'futures_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T12:08:51.103000',
                        's': 'BTCUSD_PERP',
                        'p': 49214.9,
                        'p24': 51335.5,
                        'dt': -4.13,
                        'fp': 0.0020319049718682757,
                        'bip': 0.0,
                        'asp': 0.0,
                        're': True,
                        'v24': 342444.0,
                        'mp': 0.0,
                        'hip': 55487.2,
                        'lop': 47014.3,
                        'exp': 'None',
                        'expd': 'None',
                        'pa': ['BTC', 'USD'],
                        'tck': 0.1,
                        'vt': 1.0,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.288366',
                        'mlvr': 125.0,
                    }
                ],
            }
        }
    ],
}

DEFAULT_SYMBOL_MESSAGE = {
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
    OrderSchema.futures: [
        {
            'e': '24hrTicker',
            'E': 1638964453905,
            's': 'BTCUSDT',
            'p': '-2191.41',
            'P': '-4.266',
            'w': '50649.55',
            'c': '49173.66',
            'Q': '4.291',
            'o': '51365.07',
            'h': '53900.00',
            'l': '48841.07',
            'v': '1941684.405',
            'q': '98345450001.18',
            'O': 1638878040000,
            'C': 1638964453903,
            'F': 216977693,
            'L': 217094658,
            'n': 116538,
        }
    ],
    OrderSchema.futures_coin: [
        {
            'e': '24hrTicker',
            'E': 1638965329255,
            's': 'BTCUSD_PERP',
            'ps': 'BTCUSD',
            'p': '-2120.5',
            'P': '-4.131',
            'w': '50667.10613588',
            'c': '49215.0',
            'Q': '4',
            'o': '51335.5',
            'h': '55487.2',
            'l': '47014.3',
            'v': '342441',
            'q': '675.86453247',
            'O': 1638878880000,
            'C': 1638965329244,
            'F': 50016490,
            'L': 50097295,
            'n': 80806,
        }
    ],
}
DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT = {
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
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638964453905,
                's': 'BTCUSDT',
                'p': '-2191.41',
                'P': '-4.266',
                'w': '50649.55',
                'c': '49173.66',
                'Q': '4.291',
                'o': '51365.07',
                'h': '53900.00',
                'l': '48841.07',
                'v': '1941684.405',
                'q': '98345450001.18',
                'O': 1638878040000,
                'C': 1638964453903,
                'F': 216977693,
                'L': 217094658,
                'n': 116538,
            }
        ],
    },
    OrderSchema.futures_coin: {
        'table': '24hrTicker',
        'action': 'update',
        'data': [
            {
                'e': '24hrTicker',
                'E': 1638965329255,
                's': 'BTCUSD_PERP',
                'ps': 'BTCUSD',
                'p': '-2120.5',
                'P': '-4.131',
                'w': '50667.10613588',
                'c': '49215.0',
                'Q': '4',
                'o': '51335.5',
                'h': '55487.2',
                'l': '47014.3',
                'v': '342441',
                'q': '675.86453247',
                'O': 1638878880000,
                'C': 1638965329244,
                'F': 50016490,
                'L': 50097295,
                'n': 80806,
            }
        ],
    },
}
DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT = {
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
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638964453905,
                    's': 'BTCUSDT',
                    'p': '-2191.41',
                    'P': '-4.266',
                    'w': '50649.55',
                    'c': '49173.66',
                    'Q': '4.291',
                    'o': '51365.07',
                    'h': '53900.00',
                    'l': '48841.07',
                    'v': '1941684.405',
                    'q': '98345450001.18',
                    'O': 1638878040000,
                    'C': 1638964453903,
                    'F': 216977693,
                    'L': 217094658,
                    'n': 116538,
                }
            ],
        }
    ],
    OrderSchema.futures_coin: [
        {
            'table': '24hrTicker',
            'action': 'update',
            'data': [
                {
                    'e': '24hrTicker',
                    'E': 1638965329255,
                    's': 'BTCUSD_PERP',
                    'ps': 'BTCUSD',
                    'p': '-2120.5',
                    'P': '-4.131',
                    'w': '50667.10613588',
                    'c': '49215.0',
                    'Q': '4',
                    'o': '51335.5',
                    'h': '55487.2',
                    'l': '47014.3',
                    'v': '342441',
                    'q': '675.86453247',
                    'O': 1638878880000,
                    'C': 1638965329244,
                    'F': 50016490,
                    'L': 50097295,
                    'n': 80806,
                }
            ],
        }
    ],
}
DEFAULT_SYMBOL_GET_DATA_RESULT = {
    OrderSchema.exchange: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_spot',
                'tb': 'symbol',
                'sch': 'exchange',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T11:53:44.515000',
                        's': 'BTCUSDT',
                        'p': 49155.42,
                        'p24': 51369.96,
                        'dt': -4.31,
                        'fp': 49155.42,
                        'bip': 49152.96,
                        'asp': 49152.97,
                        're': False,
                        'v24': 1038.524591,
                        'mp': 49155.42,
                        'hip': 120000.0,
                        'lop': 9782.0,
                        'exp': None,
                        'expd': None,
                        'pa': ['BTC', 'USDT'],
                        'tck': 0.01,
                        'vt': 1e-06,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.271836',
                        'mlvr': None,
                    }
                ],
            }
        }
    ],
    OrderSchema.futures: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'symbol',
                'sch': 'futures',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T11:54:13.905000',
                        's': 'BTCUSDT',
                        'p': 49173.66,
                        'p24': 51365.07000000001,
                        'dt': -4.27,
                        'fp': 49173.66,
                        'bip': 0.0,
                        'asp': 0.0,
                        're': False,
                        'v24': 1941684.405,
                        'mp': 0.0,
                        'hip': 53900.0,
                        'lop': 48841.07,
                        'exp': 'None',
                        'expd': 'None',
                        'pa': ['BTC', 'USDT'],
                        'tck': 0.01,
                        'vt': 0.001,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.272746',
                        'mlvr': 125.0,
                    }
                ],
            }
        }
    ],
    OrderSchema.futures_coin: [
        {
            'symbol': {
                'acc': 'tbinance.tbinance_futures',
                'tb': 'symbol',
                'sch': 'futures_coin',
                'act': 'update',
                'd': [
                    {
                        'tm': '2021-12-08T12:08:49.255000',
                        's': 'BTCUSD_PERP',
                        'p': 49215.0,
                        'p24': 51335.5,
                        'dt': -4.13,
                        'fp': 0.00203190084323885,
                        'bip': 0.0,
                        'asp': 0.0,
                        're': True,
                        'v24': 342441.0,
                        'mp': 0.0,
                        'hip': 55487.2,
                        'lop': 47014.3,
                        'exp': 'None',
                        'expd': 'None',
                        'pa': ['BTC', 'USD'],
                        'tck': 0.1,
                        'vt': 1.0,
                        'ss': 'btcusd',
                        'crt': '2021-09-06T09:51:21.288366',
                        'mlvr': 125.0,
                    }
                ],
            }
        }
    ],
}
