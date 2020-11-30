from tests import config as cfg

SPOT_WALLET_MESSAGE = {
    "e": "outboundAccountPosition",
    "E": 1606230225508,
    "u": 1606230225507,
    "B": [
        {"a": "BTC", "f": "1.60341000", "l": "0.00000000"},
        {"a": "USDT", "f": "8456.14550000", "l": "0.00000000"},
    ],
}
SPOT_WALLET_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "e": "outboundAccountPosition",
            "E": 1606230225508,
            "u": 1606230225507,
            "B": [
                {"a": "BTC", "f": "1.60341000", "l": "0.00000000"},
                {"a": "USDT", "f": "8456.14550000", "l": "0.00000000"},
            ],
        }
    ],
    "table": "outboundAccountPosition",
}
SPOT_WALLET_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "B": [{"a": "BTC", "f": "1.60341000", "l": "0.00000000"}],
                "E": 1606230225508,
                "e": "outboundAccountPosition",
                "u": 1606230225507,
            }
        ],
        "table": "outboundAccountPosition",
    }
]
SPOT_WALLET_GET_DATA_RESULTS = [
    {
        "wallet": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "balances": [
                        {
                            "available_margin": 1.60341,
                            "balance": 1.60341,
                            "currency": "BTC",
                            "init_margin": None,
                            "maint_margin": 0.0,
                            "margin_balance": 1.60341,
                            "type": "hold",
                            "unrealised_pnl": 0,
                        },
                    ]
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "wallet",
        }
    }
]
SPOT_PROCESS_WALLET_MESSAGE_RESULT = [
    {
        "wallet": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "balances": [
                        {
                            "available_margin": 1.60341,
                            "balance": 1.60341,
                            "currency": "BTC",
                            "init_margin": None,
                            "maint_margin": 0.0,
                            "margin_balance": 1.60341,
                            "type": "hold",
                            "unrealised_pnl": 0,
                        },
                        {
                            "available_margin": 8456.1455,
                            "balance": 8456.1455,
                            "currency": "USDT",
                            "init_margin": None,
                            "maint_margin": 0.0,
                            "margin_balance": 8456.1455,
                            "type": "hold",
                            "unrealised_pnl": 0,
                        },
                    ],
                    "total_balance": {"btc": 0.44225767, "usd": 39119.8064423},
                }
            ],
            "schema": cfg.BINANCE_SPOT_SCHEMA,
            "table": "wallet",
        }
    }
]

FUTURES_WALLET_MESSAGE = {
    "e": "ACCOUNT_UPDATE",
    "T": 1606737194206,
    "E": 1606737194209,
    "a": {
        "B": [{"a": "USDT", "wb": "99991.19288678", "cw": "99991.19288678"}],
        "P": [
            {
                "s": "BTCUSDT",
                "pa": "-1.186",
                "ep": "18564.73839",
                "cr": "-1545.14723006",
                "up": "-44.92816657",
                "mt": "cross",
                "iw": "0",
                "ps": "BOTH",
                "ma": "USDT",
            }
        ],
        "m": "ORDER",
    },
}
FUTURES_WALLET_LOOKUP_TABLE_RESULT = {
    "action": "update",
    "data": [
        {
            "E": 1606737194209,
            "T": 1606737194206,
            "a": {
                "B": [{"a": "USDT", "cw": "99991.19288678", "wb": "99991.19288678"}],
                "P": [
                    {
                        "cr": "-1545.14723006",
                        "ep": "18564.73839",
                        "iw": "0",
                        "ma": "USDT",
                        "mt": "cross",
                        "pa": "-1.186",
                        "ps": "BOTH",
                        "s": "BTCUSDT",
                        "up": "-44.92816657",
                    }
                ],
                "m": "ORDER",
            },
            "e": "ACCOUNT_UPDATE",
        }
    ],
    "table": "ACCOUNT_UPDATE",
}
FUTURES_WALLET_SPLIT_MESSAGE_RESULTS = [
    {
        "action": "update",
        "data": [
            {
                "E": 1606737194209,
                "T": 1606737194206,
                "a": {
                    "B": [
                        {"a": "USDT", "cw": "99991.19288678", "wb": "99991.19288678"}
                    ],
                    "P": [
                        {
                            "cr": "-1545.14723006",
                            "ep": "18564.73839",
                            "iw": "0",
                            "ma": "USDT",
                            "mt": "cross",
                            "pa": "-1.186",
                            "ps": "BOTH",
                            "s": "BTCUSDT",
                            "up": "-44.92816657",
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
FUTURES_WALLET_GET_DATA_RESULTS = [
    {
        "wallet": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "balances": [
                        {
                            "available_margin": 99782.05747772001,
                            "balance": 99991.19288678,
                            "borrowed": None,
                            "currency": "USDT",
                            "init_margin": 2052.59053117,
                            "interest": None,
                            "maint_margin": 164.20724249,
                            "margin_balance": 99946.26472021,
                            "type": "trade",
                            "unrealised_pnl": -44.92816657,
                        }
                    ]
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "wallet",
        }
    }
]
FUTURES_WALLET_PROCESS_MESSAGE_RESULTS = [
    {
        "wallet": {
            "account": cfg.BINANCE_ACCOUNT_NAME,
            "action": "update",
            "data": [
                {
                    "balances": [
                        {
                            "available_margin": 99782.05747772001,
                            "balance": 99991.19288678,
                            "borrowed": None,
                            "currency": "USDT",
                            "init_margin": 2052.59053117,
                            "interest": None,
                            "maint_margin": 164.20724249,
                            "margin_balance": 99946.26472021,
                            "type": "trade",
                            "unrealised_pnl": -44.92816657,
                        },
                        {
                            "available_margin": 0.0,
                            "balance": 0.0,
                            "borrowed": None,
                            "currency": "BTC",
                            "init_margin": 0.0,
                            "interest": None,
                            "maint_margin": 0.0,
                            "margin_balance": 0.0,
                            "type": "hold",
                            "unrealised_pnl": 0.0,
                            "withdraw_balance": 0.0,
                        },
                    ],
                    "total_balance": {"btc": 5.90281417, "usd": 99991.19288678},
                    "total_initial_margin": 2052.59053117,
                    "total_maint_margin": 164.20724249,
                    "total_margin_balance": {"btc": 5.90016191, "usd": 99946.26472021},
                    "total_open_order_initial_margin": 0.0,
                    "total_position_initial_margin": 2052.59053117,
                    "total_unrealised_pnl": {"btc": -0.00265226, "usd": -44.92816657},
                    "trade_enabled": True,
                }
            ],
            "schema": cfg.BINANCE_FUTURES_SCHEMA,
            "table": "wallet",
        }
    }
]
