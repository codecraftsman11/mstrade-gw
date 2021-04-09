from tests import config as cfg

FUTURES_POSITION_MESSAGE = {
    "e": "ACCOUNT_UPDATE",
    "T": 1607330722996,
    "E": 1607330722999,
    "a": {
        "B": [{"a": "USDT", "wb": "50343.25059802", "cw": "50343.25059802"}],
        "P": [
            {
                "s": "BTCUSDT",
                "pa": "-1",
                "ep": "19372.83000",
                "cr": "38805.85249994",
                "up": "124.83000000",
                "mt": "cross",
                "iw": "0",
                "ps": "BOTH",
                "ma": "USDT",
            }
        ],
        "m": "ORDER",
    },
}

FUTURES_POSITION_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "E": 1607330722999,
            "T": 1607330722996,
            "a": {
                "B": [{"a": "USDT", "cw": "50343.25059802", "wb": "50343.25059802"}],
                "P": [
                    {
                        "cr": "38805.85249994",
                        "ep": "19372.83000",
                        "iw": "0",
                        "ma": "USDT",
                        "mt": "cross",
                        "pa": "-1",
                        "ps": "BOTH",
                        "s": "BTCUSDT",
                        "up": "124.83000000",
                    }
                ],
                "m": "ORDER",
            },
            "e": "ACCOUNT_UPDATE",
        }
    ],
    "table": "ACCOUNT_UPDATE",
}

FUTURES_POSITION_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "E": 1607330722999,
                "T": 1607330722996,
                "a": {
                    "B": [
                        {"a": "USDT", "cw": "50343.25059802", "wb": "50343.25059802"}
                    ],
                    "P": [
                        {
                            "cr": "38805.85249994",
                            "ep": "19372.83000",
                            "iw": "0",
                            "ma": "USDT",
                            "mt": "cross",
                            "pa": "-1",
                            "ps": "BOTH",
                            "s": "BTCUSDT",
                            "up": "124.83000000",
                        }
                    ],
                    "m": "ORDER",
                },
                "e": "ACCOUNT_UPDATE",
            }
        ],
        "table": "ACCOUNT_UPDATE",
    }
]

FUTURES_POSITION_GET_DATA_RESULTS = [
    {
        "position": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "entry_price": 19372.83,
                    "leverage": None,
                    "leverage_type": "cross",
                    "liquidation_price": None,
                    "mark_price": None,
                    "schema": "futures",
                    "side": 1,
                    "symbol": "BTCUSDT",
                    "system_symbol": "btcusd",
                    "time": "2020-12-07 08:45:22.000000Z",
                    "timestamp": 1607330722999,
                    "unrealised_pnl": 124.83,
                    "volume": -1.0,
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "position",
        }
    }
]
