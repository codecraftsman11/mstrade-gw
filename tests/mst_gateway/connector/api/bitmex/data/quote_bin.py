from mst_gateway.connector.api import OrderSchema
from mst_gateway.connector.api.stocks.bitmex.utils import to_iso_datetime
from mst_gateway.connector.api.utils import time2timestamp


DEFAULT_QUOTE_BIN_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"tradeBin1m","action":"partial","data":[{"timestamp":"2021-12-16T08:35:00.000Z","symbol":"XBTUSD","open":48745,"high":48745,"low":48745,"close":48745,"trades":0,"volume":0,"vwap":null,"lastSize":null,"turnover":0,"homeNotional":0,"foreignNotional":0},{"timestamp":"2021-12-16T08:35:00.000Z","symbol":"XBTUSD","open":48393,"high":48393,"low":48393,"close":48393,"trades":2,"volume":2000,"vwap":48393,"lastSize":1000,"turnover":96786000,"homeNotional":0.002,"foreignNotional":96.786}]}',
            'expect': {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "tm": "2021-12-16T08:34:59.999999",
                            "s": "XBTUSD",
                            "opp": 48745.0,
                            "clp": 48745.0,
                            "hip": 48745.0,
                            "lop": 48745.0,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:35:00.000000",
                            "s": "XBTUSD",
                            "opp": 48745.0,
                            "clp": 48745.0,
                            "hip": 48745.0,
                            "lop": 48745.0,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:34:59.999999",
                            "s": "XBTUSD",
                            "opp": 48393.0,
                            "clp": 48393.0,
                            "hip": 48393.0,
                            "lop": 48393.0,
                            "vl": 2000,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:35:00.000000",
                            "s": "XBTUSD",
                            "opp": 48393.0,
                            "clp": 48393.0,
                            "hip": 48393.0,
                            "lop": 48393.0,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            'message': '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2021-12-16T08:37:00.000Z","symbol":"XBTUSD","open":48766.5,"high":48777,"low":48770,"close":48770,"trades":2,"volume":200,"vwap":48773.5881,"lastSize":100,"turnover":410059,"homeNotional":0.00410059,"foreignNotional":200}]}',
            'expect': {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-16T08:36:59.999999",
                            "s": "XBTUSD",
                            "opp": 48766.5,
                            "clp": 48770.0,
                            "hip": 48777.0,
                            "lop": 48770.0,
                            "vl": 200,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:37:00.000000",
                            "s": "XBTUSD",
                            "opp": 48770.0,
                            "clp": 48770.0,
                            "hip": 48770.0,
                            "lop": 48770.0,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }

        }
    ]
}

DEFAULT_QUOTE_BIN_MESSAGES = {
    OrderSchema.margin1: [
        {
            "table": "tradeBin1m",
            "action": "partial",
            "data": [
                {
                    "timestamp": "2021-12-16T08:35:00.000Z",
                    "symbol": "XBTUSD",
                    "open": 48745,
                    "high": 48745,
                    "low": 48745,
                    "close": 48745,
                    "trades": 0,
                    "volume": 0,
                    "vwap": None,
                    "lastSize": None,
                    "turnover": 0,
                    "homeNotional": 0,
                    "foreignNotional": 0
                },
                {
                    "timestamp": "2021-12-16T08:35:00.000Z",
                    "symbol": "XBTUSD",
                    "open": 48393,
                    "high": 48393,
                    "low": 48393,
                    "close": 48393,
                    "trades": 2,
                    "volume": 2000,
                    "vwap": 48393,
                    "lastSize": 1000,
                    "turnover": 96786000,
                    "homeNotional": 0.002,
                    "foreignNotional": 96.786
                },
            ]
        },
        {
            "table": "tradeBin1m",
            "action": "insert",
            "data": [
                {
                    "timestamp": "2021-12-16T08:37:00.000Z",
                    "symbol": "XBTUSD",
                    "open": 48766.5,
                    "high": 48777,
                    "low": 48770,
                    "close": 48770,
                    "trades": 2,
                    "volume": 200,
                    "vwap": 48773.5881,
                    "lastSize": 100,
                    "turnover": 410059,
                    "homeNotional": 0.00410059,
                    "foreignNotional": 200
                }
            ]
        }
    ]
}

TEST_QUOTE_BIN_MESSAGES = [
    {
        'message': '{"table": "trade", "action": "invalid"}',
        'data': None,
        'data_trade': None
    },
    {
        'message': '{"table":"trade","action":"partial","data":[{"timestamp":"2019-07-01T10:29:04.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': None,
        'data_trade': None
    },
    {
        'message': '{"table":"tradeBin1m","action":"partial","data":[{"timestamp":"2019-07-01T10:30:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "partial",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T10:30:00.000Z"),
                    'timestamp': time2timestamp("2019-07-01T10:30:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "partial",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T10:30:00.000Z"),
                    'timestamp': time2timestamp("2019-07-01T10:30:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:58:09.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:58:09.589Z"),
                    'timestamp': time2timestamp("2019-07-01T11:58:09.589Z"),
                    'symbol': "XBTUSD",
                    'volume': 20,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:58:09.589Z"),
                    'timestamp': time2timestamp("2019-07-01T11:58:09.589Z"),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
    },
    {
        'message': '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2019-07-01T11:59:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:59:00.000Z"),
                    'timestamp': time2timestamp("2019-07-01T11:59:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
        'data_trade': None
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:36.307Z","symbol":"XBTUSD","side":"Sell","size":100,"price":11329,"tickDirection":"MinusTick","trdMatchID":"4e2522dc-c411-46dc-7f2f-e33491965ddd","grossValue":882700,"homeNotional":0.008827,"foreignNotional":100}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:59:36.307Z"),
                    'timestamp': time2timestamp("2019-07-01T11:59:36.307Z"),
                    'symbol': "XBTUSD",
                    'volume': 200,
                    'open': 11329,
                    'close': 11329,
                    'low': 11329,
                    'high': 11329,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:59:36.307Z"),
                    'timestamp': time2timestamp("2019-07-01T11:59:36.307Z"),
                    'symbol': "XBTUSD",
                    'volume': 100,
                    'open': 11329,
                    'close': 11329,
                    'low': 11329,
                    'high': 11329,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        }
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:38.326Z","symbol":"XBTUSD","side":"Sell","size":5,"price":11339,"tickDirection":"ZeroMinusTick","trdMatchID":"1084f572-05d1-c16d-d5d3-02d5f8a9bbbb","grossValue":44135,"homeNotional":0.00044135,"foreignNotional":5}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:59:38.326Z"),
                    'timestamp': time2timestamp("2019-07-01T11:59:38.326Z"),
                    'symbol': "XBTUSD",
                    'volume': 210,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'schema': OrderSchema.margin1,
            'action': "update",
            'data': [
                {
                    'time': to_iso_datetime("2019-07-01T11:59:38.326Z"),
                    'timestamp': time2timestamp("2019-07-01T11:59:38.326Z"),
                    'symbol': "XBTUSD",
                    'volume': 110,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339,
                    'system_symbol': 'btcusd',
                    'schema': 'margin1'
                }
            ]
        }
    }
]

TEST_QUOTE_BIN_STATE = {
    'account': "bitmex.test",
    'table': "quote_bin",
    'schema': OrderSchema.margin1,
    'action': "partial",
    'data': [
        {
            'time': to_iso_datetime("2019-07-01T11:59:38.326Z"),
            'timestamp': time2timestamp("2019-07-01T11:59:38.326Z"),
            'symbol': "XBTUSD",
            'volume': 210,
            'open': 11329,
            'close': 11339,
            'low': 11329,
            'high': 11339,
            'system_symbol': 'btcusd',
            'schema': 'margin1'
        }
    ]
}
