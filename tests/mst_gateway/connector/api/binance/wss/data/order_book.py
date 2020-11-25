from tests import config as cfg

SPOT_ORDER_BOOK_MESSAGE = {
    "e": "depthUpdate",
    "E": 1606136814064,
    "s": "BTCUSDT",
    "U": 7208749,
    "u": 7208752,
    "b": [["30.70000000", "0.00000000"], ["30.69330000", "0.42000000"]],
    "a": [["30.70010000", "7.10000000"], ["30.70510000", "0.00000000"]],
}
SPOT_ORDER_BOOK_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "depthUpdate",
            "E": 1606136814064,
            "s": "BTCUSDT",
            "U": 7208749,
            "u": 7208752,
            "b": [["30.70000000", "0.00000000"], ["30.69330000", "0.42000000"]],
            "a": [["30.70010000", "7.10000000"], ["30.70510000", "0.00000000"]],
        }
    ],
    "table": "depthUpdate",
}
SPOT_ORDER_BOOK_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "delete",
        "data": [
            {
                "E": 1606136814064,
                "U": 7208749,
                "b": ["30.69330000", "0.42000000"],
                "e": "depthUpdate",
                "s": "BTCUSDT",
                "u": 7208752,
            },
            {
                "E": 1606136814064,
                "U": 7208749,
                "a": ["30.70010000", "7.10000000"],
                "e": "depthUpdate",
                "s": "BTCUSDT",
                "u": 7208752,
            },
        ],
        "table": "depthUpdate",
    },
    {
        "action": "update",
        "data": [
            {
                "E": 1606136814064,
                "U": 7208749,
                "b": ["30.70000000", "0.00000000"],
                "e": "depthUpdate",
                "s": "BTCUSDT",
                "u": 7208752,
            },
            {
                "E": 1606136814064,
                "U": 7208749,
                "a": ["30.70510000", "0.00000000"],
                "e": "depthUpdate",
                "s": "BTCUSDT",
                "u": 7208752,
            },
        ],
        "table": "depthUpdate",
    },
]
SPOT_ORDER_BOOK_GET_DATA_RESULTS = [
    {
        "order_book": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "delete",
            "data": [
                {
                    "id": 390711081372756,
                    "price": 30.6933,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 0,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "volume": 0.42,
                },
                {
                    "id": 390711080692756,
                    "price": 30.7001,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 1,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "volume": 7.1,
                },
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "order_book",
        }
    },
    {
        "order_book": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "id": 390711080702756,
                    "price": 30.7,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 0,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "volume": 0.0,
                },
                {
                    "id": 390711080192756,
                    "price": 30.7051,
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "side": 1,
                    "symbol": "btcusdt",
                    "system_symbol": "btcusd",
                    "volume": 0.0,
                },
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "order_book",
        }
    },
]
