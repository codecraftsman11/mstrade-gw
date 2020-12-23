from tests import config as cfg

SPOT_SYMBOL_DETAIL_MESSAGE = {
    "e": "24hrTicker",
    "E": 1606124519688,
    "s": "BTCUSDT",
    "p": "-490.00000000",
    "P": "-49.000",
    "w": "678.61510386",
    "x": "1000.00000000",
    "c": "510.00000000",
    "Q": "0.10000000",
    "b": "510.00000000",
    "B": "17.94814500",
    "a": "0.00000000",
    "A": "0.00000000",
    "o": "1000.00000000",
    "h": "2550.00000000",
    "l": "500.00000000",
    "v": "3.34600000",
    "q": "2270.64613750",
    "O": 1606034464182,
    "C": 1606120864182,
    "F": 1142,
    "L": 1161,
    "n": 20,
}
SPOT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "24hrTicker",
            "E": 1606124519688,
            "s": "BTCUSDT",
            "p": "-490.00000000",
            "P": "-49.000",
            "w": "678.61510386",
            "x": "1000.00000000",
            "c": "510.00000000",
            "Q": "0.10000000",
            "b": "510.00000000",
            "B": "17.94814500",
            "a": "0.00000000",
            "A": "0.00000000",
            "o": "1000.00000000",
            "h": "2550.00000000",
            "l": "500.00000000",
            "v": "3.34600000",
            "q": "2270.64613750",
            "O": 1606034464182,
            "C": 1606120864182,
            "F": 1142,
            "L": 1161,
            "n": 20,
        }
    ],
    "table": "24hrTicker",
}
SPOT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "e": "24hrTicker",
                "E": 1606124519688,
                "s": "BTCUSDT",
                "p": "-490.00000000",
                "P": "-49.000",
                "w": "678.61510386",
                "x": "1000.00000000",
                "c": "510.00000000",
                "Q": "0.10000000",
                "b": "510.00000000",
                "B": "17.94814500",
                "a": "0.00000000",
                "A": "0.00000000",
                "o": "1000.00000000",
                "h": "2550.00000000",
                "l": "500.00000000",
                "v": "3.34600000",
                "q": "2270.64613750",
                "O": 1606034464182,
                "C": 1606120864182,
                "F": 1142,
                "L": 1161,
                "n": 20,
            }
        ],
        "table": "24hrTicker",
    }
]
SPOT_SYMBOL_DETAIL_GET_DATA_RESULTS = [
    {
        "symbol": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "ask_price": 0.0,
                    "bid_price": 510.0,
                    "created": "2020-11-24 15:48:26.432914Z",
                    "delta": -24.85,
                    "expiration": None,
                    "face_price": 510.0,
                    "pair": ["BTC", "USDT"],
                    "price": 510.0,
                    "price24": 678.61510386,
                    "reversed": False,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol": "BTCUSDT",
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "system_symbol": "btcusd",
                    "tick": 0.01,
                    "time": "2020-11-23 09:41:59.000000Z",
                    "timestamp": 1606124519688,
                    "volume24": 3.346,
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "symbol",
        }
    }
]

SPOT_SYMBOL_MESSAGE = [
    {
        "e": "24hrTicker",
        "E": 1606124498337,
        "s": "BTCUSDT",
        "p": "0.72700000",
        "P": "2.417",
        "w": "30.18978584",
        "x": "30.08150000",
        "c": "30.81010000",
        "Q": "1.70000000",
        "b": "30.81000000",
        "B": "3.24000000",
        "a": "30.81250000",
        "A": "1.04000000",
        "o": "30.08310000",
        "h": "31.04390000",
        "l": "29.00000000",
        "v": "8786.81000000",
        "q": "265271.91207900",
        "O": 1606038098336,
        "C": 1606124498336,
        "F": 39138,
        "L": 48365,
        "n": 9228,
    },
    {
        "e": "24hrTicker",
        "E": 1606124498763,
        "s": "BTCUSDT",
        "p": "-490.00000000",
        "P": "-49.000",
        "w": "678.61510386",
        "x": "1000.00000000",
        "c": "510.00000000",
        "Q": "0.10000000",
        "b": "510.00000000",
        "B": "17.94814500",
        "a": "0.00000000",
        "A": "0.00000000",
        "o": "1000.00000000",
        "h": "2550.00000000",
        "l": "500.00000000",
        "v": "3.34600000",
        "q": "2270.64613750",
        "O": 1606034464182,
        "C": 1606120864182,
        "F": 1142,
        "L": 1161,
        "n": 20,
    },
]
SPOT_SYMBOL_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "24hrTicker",
            "E": 1606124498337,
            "s": "BTCUSDT",
            "p": "0.72700000",
            "P": "2.417",
            "w": "30.18978584",
            "x": "30.08150000",
            "c": "30.81010000",
            "Q": "1.70000000",
            "b": "30.81000000",
            "B": "3.24000000",
            "a": "30.81250000",
            "A": "1.04000000",
            "o": "30.08310000",
            "h": "31.04390000",
            "l": "29.00000000",
            "v": "8786.81000000",
            "q": "265271.91207900",
            "O": 1606038098336,
            "C": 1606124498336,
            "F": 39138,
            "L": 48365,
            "n": 9228,
        },
        {
            "e": "24hrTicker",
            "E": 1606124498763,
            "s": "BTCUSDT",
            "p": "-490.00000000",
            "P": "-49.000",
            "w": "678.61510386",
            "x": "1000.00000000",
            "c": "510.00000000",
            "Q": "0.10000000",
            "b": "510.00000000",
            "B": "17.94814500",
            "a": "0.00000000",
            "A": "0.00000000",
            "o": "1000.00000000",
            "h": "2550.00000000",
            "l": "500.00000000",
            "v": "3.34600000",
            "q": "2270.64613750",
            "O": 1606034464182,
            "C": 1606120864182,
            "F": 1142,
            "L": 1161,
            "n": 20,
        },
    ],
    "table": "24hrTicker",
}
SPOT_SYMBOL_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "e": "24hrTicker",
                "E": 1606124498337,
                "s": "BTCUSDT",
                "p": "0.72700000",
                "P": "2.417",
                "w": "30.18978584",
                "x": "30.08150000",
                "c": "30.81010000",
                "Q": "1.70000000",
                "b": "30.81000000",
                "B": "3.24000000",
                "a": "30.81250000",
                "A": "1.04000000",
                "o": "30.08310000",
                "h": "31.04390000",
                "l": "29.00000000",
                "v": "8786.81000000",
                "q": "265271.91207900",
                "O": 1606038098336,
                "C": 1606124498336,
                "F": 39138,
                "L": 48365,
                "n": 9228,
            },
            {
                "e": "24hrTicker",
                "E": 1606124498763,
                "s": "BTCUSDT",
                "p": "-490.00000000",
                "P": "-49.000",
                "w": "678.61510386",
                "x": "1000.00000000",
                "c": "510.00000000",
                "Q": "0.10000000",
                "b": "510.00000000",
                "B": "17.94814500",
                "a": "0.00000000",
                "A": "0.00000000",
                "o": "1000.00000000",
                "h": "2550.00000000",
                "l": "500.00000000",
                "v": "3.34600000",
                "q": "2270.64613750",
                "O": 1606034464182,
                "C": 1606120864182,
                "F": 1142,
                "L": 1161,
                "n": 20,
            },
        ],
        "table": "24hrTicker",
    }
]
SPOT_SYMBOL_GET_DATA_RESULTS = [
    {
        "symbol": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "ask_price": 30.8125,
                    "bid_price": 30.81,
                    "created": "2020-11-24 15:53:54.000000Z",
                    "delta": 2.05,
                    "expiration": None,
                    "face_price": 30.8101,
                    "pair": ["BTC", "USDT"],
                    "price": 30.8101,
                    "price24": 30.18978584,
                    "reversed": False,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol": "BTCUSDT",
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "system_symbol": "btcusd",
                    "tick": 0.01,
                    "time": "2020-11-23 09:41:38.000000Z",
                    "timestamp": 1606124498337,
                    "volume24": 8786.81,
                },
                {
                    "ask_price": 0.0,
                    "bid_price": 510.0,
                    "created": "2020-11-24 15:53:54.000000Z",
                    "delta": -24.85,
                    "expiration": None,
                    "face_price": 510.0,
                    "pair": ["BTC", "USDT"],
                    "price": 510.0,
                    "price24": 678.61510386,
                    "reversed": False,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol": "BTCUSDT",
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "system_symbol": "btcusd",
                    "tick": 0.01,
                    "time": "2020-11-23 09:41:38.000000Z",
                    "timestamp": 1606124498763,
                    "volume24": 3.346,
                },
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "symbol",
        }
    },
]

FUTURES_SYMBOL_MESSAGE = [
    {
        "e": "24hrTicker",
        "E": 1606745796712,
        "s": "BTCUSDT",
        "p": "840.00",
        "P": "4.626",
        "w": "18515.75",
        "c": "19000.00",
        "Q": "1.630",
        "o": "18160.00",
        "h": "80240.00",
        "l": "18.00",
        "v": "88743.677",
        "q": "1643155365.64",
        "O": 1606659360000,
        "C": 1606745796709,
        "F": 147461070,
        "L": 147482123,
        "n": 20799,
    }
]
FUTURES_SYMBOL_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "C": 1606745796709,
            "E": 1606745796712,
            "F": 147461070,
            "L": 147482123,
            "O": 1606659360000,
            "P": "4.626",
            "Q": "1.630",
            "c": "19000.00",
            "e": "24hrTicker",
            "h": "80240.00",
            "l": "18.00",
            "n": 20799,
            "o": "18160.00",
            "p": "840.00",
            "q": "1643155365.64",
            "s": "BTCUSDT",
            "v": "88743.677",
            "w": "18515.75",
        }
    ],
    "table": "24hrTicker",
}
FUTURES_SYMBOL_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "C": 1606745796709,
                "E": 1606745796712,
                "F": 147461070,
                "L": 147482123,
                "O": 1606659360000,
                "P": "4.626",
                "Q": "1.630",
                "c": "19000.00",
                "e": "24hrTicker",
                "h": "80240.00",
                "l": "18.00",
                "n": 20799,
                "o": "18160.00",
                "p": "840.00",
                "q": "1643155365.64",
                "s": "BTCUSDT",
                "v": "88743.677",
                "w": "18515.75",
            }
        ],
        "table": "24hrTicker",
    }
]
FUTURES_SYMBOL_GET_DATA_RESULTS = [
    {
        "symbol": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "ask_price": None,
                    "bid_price": None,
                    "created": "2020-09-29 11:24:02.687353Z",
                    "delta": 2.62,
                    "expiration": None,
                    "face_price": 19000.0,
                    "pair": ["BTC", "USDT"],
                    "price": 19000.0,
                    "price24": 18515.75,
                    "reversed": False,
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol": "BTCUSDT",
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "system_symbol": "btcusd",
                    "tick": 0.01,
                    "time": "2020-11-30 14:16:36.000000Z",
                    "timestamp": 1606745796712,
                    "volume24": 88743.677,
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "symbol",
        }
    }
]
