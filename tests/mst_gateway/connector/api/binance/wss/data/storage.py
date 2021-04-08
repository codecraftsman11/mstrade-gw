from datetime import datetime, timezone
from tests import config as cfg

STORAGE_DATA = {
    "symbol": {
        cfg.BINANCE_WSS_API_NAME: {
            cfg.BINANCE_SPOT_SCHEMA: {
                "btcusdt": {
                    "tick": 0.01,
                    "volume_tick": 0.01,
                    "pair": ["BTC", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686572, tzinfo=timezone.utc
                    ),
                    "system_symbol": "btcusd",
                    "symbol": "btcusdt",
                    "exchange": "Binance",
                    "max_leverage": None,
                },
                "ethusdt": {
                    "tick": 0.01,
                    "volume_tick": 0.01,
                    "pair": ["ETH", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686628, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ethusd",
                    "symbol": "ethusdt",
                    "exchange": "Binance",
                    "max_leverage": None,
                }
            },
            cfg.BINANCE_FUTURES_SCHEMA: {
                "btcusdt": {
                    "tick": 0.01,
                    "volume_tick": 0.01,
                    "pair": ["BTC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687353, tzinfo=timezone.utc
                    ),
                    "system_symbol": "btcusd",
                    "symbol": "btcusdt",
                    "exchange": "Binance",
                    "max_leverage": 50,
                },
                "ethusdt": {
                    "tick": 0.01,
                    "volume_tick": 0.01,
                    "pair": ["ETH", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687408, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ethusd",
                    "symbol": "ethusdt",
                    "exchange": "Binance",
                    "max_leverage": 50,
                },
            },
        },
    },
    f"wallet.{cfg.BINANCE_ACCOUNT_ID}": {
        "app_prefix": 1606230664,
        cfg.BINANCE_SPOT_SCHEMA: {
            "balances": {
                "btc": {
                    "currency": "BTC",
                    "balance": 1.701654,
                    "withdraw_balance": 1.701654,
                    "unrealised_pnl": 0,
                    "margin_balance": 1.701654,
                    "maint_margin": 0.0,
                    "init_margin": None,
                    "available_margin": 1.701654,
                    "type": "hold",
                },
                "usdt": {
                    "currency": "USDT",
                    "balance": 8215.4477,
                    "withdraw_balance": 8215.4477,
                    "unrealised_pnl": 0,
                    "margin_balance": 8215.4477,
                    "maint_margin": 0.0,
                    "init_margin": None,
                    "available_margin": 8215.4477,
                    "type": "hold",
                },
            },
            "total_balance": {"btc": 8217.149354, "usd": 8215.4477},
        },
        cfg.BINANCE_FUTURES_SCHEMA: {
            "trade_enabled": True,
            "total_initial_margin": 2052.59053117,
            "total_maint_margin": 164.20724249,
            "total_open_order_initial_margin": 0.0,
            "total_position_initial_margin": 2052.59053117,
            "balances": {
                "usdt": {
                    "currency": "USDT",
                    "balance": 99983.85959878,
                    "withdraw_balance": 97230.4581571,
                    "borrowed": None,
                    "interest": None,
                    "unrealised_pnl": -700.81091051,
                    "margin_balance": 99283.04868827,
                    "maint_margin": 164.20724249,
                    "init_margin": 2052.59053117,
                    "available_margin": 99118.84144578,
                    "type": "trade",
                },
                "btc": {
                    "currency": "BTC",
                    "balance": 0.0,
                    "withdraw_balance": 0.0,
                    "borrowed": None,
                    "interest": None,
                    "unrealised_pnl": 0.0,
                    "margin_balance": 0.0,
                    "maint_margin": 0.0,
                    "init_margin": 0.0,
                    "available_margin": 0.0,
                    "type": "hold",
                },
            },
            "total_balance": {"btc": 5.90238126, "usd": 99983.85959878},
            "total_unrealised_pnl": {"btc": -0.04137121, "usd": -700.81091051},
            "total_margin_balance": {"btc": 5.86101005, "usd": 99283.04868827},
        },
    },
    "currency": {
        cfg.BINANCE_WSS_API_NAME: {
            cfg.BINANCE_SPOT_SCHEMA: {"btcusdt": 19124.03},
            cfg.BINANCE_FUTURES_SCHEMA: {"btcusdt": 16939.58},
        },
    },
}
