from tests import config as cfg

SPOT_QUOTE_BIN_MESSAGE = {
    "e": "kline",
    "E": 1606125552342,
    "s": "BTCUSDT",
    "k": {
        "t": 1606125540000,
        "T": 1606125599999,
        "s": "BTCUSDT",
        "i": "1m",
        "f": 48569,
        "L": 48574,
        "o": "31.05520000",
        "c": "31.07250000",
        "h": "31.07250000",
        "l": "31.05520000",
        "v": "8.32000000",
        "n": 6,
        "x": False,
        "q": "258.41617500",
        "V": "8.32000000",
        "Q": "258.41617500",
        "B": "0",
    },
}
SPOT_QUOTE_BIN_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "kline",
            "E": 1606125552342,
            "s": "BTCUSDT",
            "k": {
                "t": 1606125540000,
                "T": 1606125599999,
                "s": "BTCUSDT",
                "i": "1m",
                "f": 48569,
                "L": 48574,
                "o": "31.05520000",
                "c": "31.07250000",
                "h": "31.07250000",
                "l": "31.05520000",
                "v": "8.32000000",
                "n": 6,
                "x": False,
                "q": "258.41617500",
                "V": "8.32000000",
                "Q": "258.41617500",
                "B": "0",
            },
        }
    ],
    "table": "kline",
}
SPOT_QUOTE_BIN_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "e": "kline",
                "E": 1606125552342,
                "s": "BTCUSDT",
                "k": {
                    "t": 1606125540000,
                    "T": 1606125599999,
                    "s": "BTCUSDT",
                    "i": "1m",
                    "f": 48569,
                    "L": 48574,
                    "o": "31.05520000",
                    "c": "31.07250000",
                    "h": "31.07250000",
                    "l": "31.05520000",
                    "v": "8.32000000",
                    "n": 6,
                    "x": False,
                    "q": "258.41617500",
                    "V": "8.32000000",
                    "Q": "258.41617500",
                    "B": "0",
                },
            }
        ],
        "table": "kline",
    }
]
SPOT_QUOTE_BIN_GET_DATA_RESULTS = [
    {
        "quote_bin": {
            "account": cfg.BINANCE_WSS_API_NAME,
            "action": "update",
            "data": [
                {
                    "close": 31.0725,
                    "high": 31.0725,
                    "low": 31.0552,
                    "open": 31.0552,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "time": "2020-11-23 09:59:00.000000Z",
                    "timestamp": 1606125540000,
                    "volume": 8.32,
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "quote_bin",
        }
    }
]

FUTURES_QUOTE_BIN_MESSAGE = {
    "e": "kline",
    "E": 1606739342001,
    "s": "BTCUSDT",
    "k": {
        "t": 1606739280000,
        "T": 1606739339999,
        "s": "BTCUSDT",
        "i": "1m",
        "f": -1,
        "L": -1,
        "o": "22792.59",
        "c": "22792.59",
        "h": "22792.59",
        "l": "22792.59",
        "v": "0.000",
        "n": 0,
        "x": True,
        "q": "0.00000",
        "V": "0.000",
        "Q": "0.00000",
        "B": "0",
    },
}
FUTURES_QUOTE_BIN_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "E": 1606739342001,
            "e": "kline",
            "k": {
                "B": "0",
                "L": -1,
                "Q": "0.00000",
                "T": 1606739339999,
                "V": "0.000",
                "c": "22792.59",
                "f": -1,
                "h": "22792.59",
                "i": "1m",
                "l": "22792.59",
                "n": 0,
                "o": "22792.59",
                "q": "0.00000",
                "s": "BTCUSDT",
                "t": 1606739280000,
                "v": "0.000",
                "x": True,
            },
            "s": "BTCUSDT",
        }
    ],
    "table": "kline",
}
FUTURES_QUOTE_BIN_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "E": 1606739342001,
                "e": "kline",
                "k": {
                    "B": "0",
                    "L": -1,
                    "Q": "0.00000",
                    "T": 1606739339999,
                    "V": "0.000",
                    "c": "22792.59",
                    "f": -1,
                    "h": "22792.59",
                    "i": "1m",
                    "l": "22792.59",
                    "n": 0,
                    "o": "22792.59",
                    "q": "0.00000",
                    "s": "BTCUSDT",
                    "t": 1606739280000,
                    "v": "0.000",
                    "x": True,
                },
                "s": "BTCUSDT",
            }
        ],
        "table": "kline",
    }
]
FUTURES_QUOTE_BIN_GET_DATA_RESULTS = [
    {
        "quote_bin": {
            "account": cfg.BINANCE_WSS_API_NAME,
            "action": "update",
            "data": [
                {
                    "close": 22792.59,
                    "high": 22792.59,
                    "low": 22792.59,
                    "open": 22792.59,
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "time": "2020-11-30 12:28:00.000000Z",
                    "timestamp": 1606739280000,
                    "volume": 0.0,
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "quote_bin",
        }
    }
]
