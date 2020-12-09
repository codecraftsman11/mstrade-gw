from tests import config as cfg

SPOT_TRADE_MESSAGE = {
    "e": "trade",
    "E": 1606125171321,
    "s": "BTCUSDT",
    "t": 48481,
    "p": "30.83080000",
    "q": "0.80000000",
    "b": 3608270,
    "a": 3608267,
    "T": 1606125171320,
    "m": False,
    "M": True,
}
SPOT_TRADE_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "trade",
            "E": 1606125171321,
            "s": "BTCUSDT",
            "t": 48481,
            "p": "30.83080000",
            "q": "0.80000000",
            "b": 3608270,
            "a": 3608267,
            "T": 1606125171320,
            "m": False,
            "M": True,
        }
    ],
    "table": "trade",
}
SPOT_TRADE_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "e": "trade",
                "E": 1606125171321,
                "s": "BTCUSDT",
                "t": 48481,
                "p": "30.83080000",
                "q": "0.80000000",
                "b": 3608270,
                "a": 3608267,
                "T": 1606125171320,
                "m": False,
                "M": True,
            }
        ],
        "table": "trade",
    }
]
SPOT_TRADE_GET_DATA_RESULTS = [
    {
        "trade": {
            "account": "binance.binance",
            "action": "update",
            "data": [
                {
                    "price": 30.8308,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 1,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "time": "2020-11-23 09:52:51.000000Z",
                    "timestamp": 1606125171321,
                    "volume": 0.8,
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "trade",
        }
    }
]

FUTURES_TRADE_MESSAGE = {
    "e": "trade",
    "E": 1606739270522,
    "T": 1606739270519,
    "s": "BTCUSDT",
    "t": 147481536,
    "p": "22792.59",
    "q": "1.504",
    "X": "MARKET",
    "m": False,
}
FUTURES_TRADE_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "E": 1606739270522,
            "T": 1606739270519,
            "X": "MARKET",
            "e": "trade",
            "m": False,
            "p": "22792.59",
            "q": "1.504",
            "s": "BTCUSDT",
            "t": 147481536,
        }
    ],
    "table": "trade",
}
FUTURES_TRADE_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "E": 1606739270522,
                "T": 1606739270519,
                "X": "MARKET",
                "e": "trade",
                "m": False,
                "p": "22792.59",
                "q": "1.504",
                "s": "BTCUSDT",
                "t": 147481536,
            }
        ],
        "table": "trade",
    }
]
FUTURES_TRADE_GET_DATA_RESULTS = [
    {
        "trade": {
            "account": "binance.binance",
            "action": "update",
            "data": [
                {
                    "price": 22792.59,
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "side": 1,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "time": "2020-11-30 12:27:50.000000Z",
                    "timestamp": 1606739270522,
                    "volume": 1.504,
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "trade",
        }
    }
]
