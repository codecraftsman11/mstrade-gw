from mst_gateway.connector.api.stocks.bitmex.utils import _date
from mst_gateway.connector.api.utils import time2timestamp
from mst_gateway.connector import api


TEST_TRADE_MESSAGES = [
    {
        'message': '{"table": "trade", "action": "invalid"}',
        'data': None,
        'data_quote': None
    },
    {
        'message': '{"table":"trade","action":"partial","data":[{"timestamp":"2019-07-01T10:29:04.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': {
            'account': "bitmex.test",
            'table': "trade",
            'action': "partial",
            'data': [
                {
                    'time': _date("2019-07-01T10:29:04.589Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T10:29:04.589Z")),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'price': 11397.5,
                    'side': api.BUY
                }
            ]
        },
        'data_quote': None,
    },
    {
        'message': '{"table":"tradeBin1m","action":"partial","data":[{"timestamp":"2019-07-01T10:30:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': None,
        'data_quote': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "partial",
            'data': [
                {
                    'time': _date("2019-07-01T10:30:00.000Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T10:30:00.000Z")),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        },
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:58:09.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': {
            'account': "bitmex.test",
            'table': "trade",
            'action': "insert",
            'data': [
                {
                    'time': _date("2019-07-01T11:58:09.589Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:58:09.589Z")),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'price': 11397.5,
                    'side': api.BUY
                }
            ]
        },
        'data_quote': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "update",
            'data': [
                {
                    'time': _date("2019-07-01T11:58:09.589Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:58:09.589Z")),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                }
            ]
        },
    },
    {
        'message': '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2019-07-01T11:59:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': None,
        'data_quote': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "update",
            'data': [
                {
                    'time': _date("2019-07-01T11:59:00.000Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:59:00.000Z")),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        },
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:36.307Z","symbol":"XBTUSD","side":"Sell","size":100,"price":11329,"tickDirection":"MinusTick","trdMatchID":"4e2522dc-c411-46dc-7f2f-e33491965ddd","grossValue":882700,"homeNotional":0.008827,"foreignNotional":100}]}',
        'data': {
            'account': "bitmex.test",
            'table': "trade",
            'action': "insert",
            'data': [
                {
                    'time': _date("2019-07-01T11:59:36.307Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:59:36.307Z")),
                    'symbol': "XBTUSD",
                    'volume': 100,
                    'price': 11329,
                    'side': api.SELL
                }
            ]
        },
        'data_quote': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "update",
            'data': [
                {
                    'time': _date("2019-07-01T11:59:36.307Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:59:36.307Z")),
                    'symbol': "XBTUSD",
                    'volume': 100,
                    'open': 11329,
                    'close': 11329,
                    'low': 11329,
                    'high': 11329
                }
            ]
        },
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:38.326Z","symbol":"XBTUSD","side":"Sell","size":5,"price":11339,"tickDirection":"ZeroMinusTick","trdMatchID":"1084f572-05d1-c16d-d5d3-02d5f8a9bbbb","grossValue":44135,"homeNotional":0.00044135,"foreignNotional":5}]}',
        'data': {
            'account': "bitmex.test",
            'table': "trade",
            'action': "insert",
            'data': [
                {
                    'time': _date("2019-07-01T11:59:38.326Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:59:38.326Z")),
                    'symbol': "XBTUSD",
                    'volume': 5,
                    'price': 11339,
                    'side': api.SELL
                }
            ]
        },
        'data_quote': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "update",
            'data': [
                {
                    'time': _date("2019-07-01T11:59:38.326Z"),
                    'timestamp': time2timestamp(_date("2019-07-01T11:59:38.326Z")),
                    'symbol': "XBTUSD",
                    'volume': 105,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339
                }
            ]
        },
    }
]
