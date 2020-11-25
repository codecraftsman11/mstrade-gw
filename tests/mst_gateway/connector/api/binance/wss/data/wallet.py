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
