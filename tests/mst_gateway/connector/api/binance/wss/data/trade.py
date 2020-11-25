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
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "price": 30.8308,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 1,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "time": "2020-11-23 11:52:51.321000Z",
                    "timestamp": 1606125171321,
                    "volume": 0.8,
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "trade",
        }
    }
]
