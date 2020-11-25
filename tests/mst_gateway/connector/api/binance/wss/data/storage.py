from datetime import datetime, timezone
from tests import config as cfg

STORAGE_DATA = {
    "symbol": {
        cfg.BINANCE_WSS_API_NAME: {
            cfg.BINANCE_SPOT_SCHEMA: {
                "ethbtc": {
                    "tick": 1e-06,
                    "pair": ["ETH", "BTC"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686903, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ethbtc",
                    "symbol": "ethbtc",
                    "exchange": "Binance",
                },
                "ltcbtc": {
                    "tick": 1e-06,
                    "pair": ["LTC", "BTC"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686958, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ltcbtc",
                    "symbol": "ltcbtc",
                    "exchange": "Binance",
                },
                "bnbbtc": {
                    "tick": 1e-07,
                    "pair": ["BNB", "BTC"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686848, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bnbbtc",
                    "symbol": "bnbbtc",
                    "exchange": "Binance",
                },
                "btcusdt": {
                    "tick": 0.01,
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
                },
                "ethusdt": {
                    "tick": 0.01,
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
                },
                "trxbtc": {
                    "tick": 1e-08,
                    "pair": ["TRX", "BTC"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687012, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trxbtc",
                    "symbol": "trxbtc",
                    "exchange": "Binance",
                },
                "xrpbtc": {
                    "tick": 1e-08,
                    "pair": ["XRP", "BTC"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687066, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xrpbtc",
                    "symbol": "xrpbtc",
                    "exchange": "Binance",
                },
                "bnbusdt": {
                    "tick": 0.0001,
                    "pair": ["BNB", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686516, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bnbusd",
                    "symbol": "bnbusdt",
                    "exchange": "Binance",
                },
                "ltcusdt": {
                    "tick": 0.01,
                    "pair": ["LTC", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686683, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ltcusd",
                    "symbol": "ltcusdt",
                    "exchange": "Binance",
                },
                "ltcbnb": {
                    "tick": 0.001,
                    "pair": ["LTC", "BNB"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687121, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ltcbnb",
                    "symbol": "ltcbnb",
                    "exchange": "Binance",
                },
                "xrpusdt": {
                    "tick": 1e-05,
                    "pair": ["XRP", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686794, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xrpusd",
                    "symbol": "xrpusdt",
                    "exchange": "Binance",
                },
                "xrpbnb": {
                    "tick": 1e-05,
                    "pair": ["XRP", "BNB"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687297, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xrpbnb",
                    "symbol": "xrpbnb",
                    "exchange": "Binance",
                },
                "trxbnb": {
                    "tick": 1e-06,
                    "pair": ["TRX", "BNB"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687228, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trxbnb",
                    "symbol": "trxbnb",
                    "exchange": "Binance",
                },
                "trxusdt": {
                    "tick": 1e-05,
                    "pair": ["TRX", "USDT"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686739, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trxusd",
                    "symbol": "trxusdt",
                    "exchange": "Binance",
                },
                "bnbbusd": {
                    "tick": 0.0001,
                    "pair": ["BNB", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686092, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bnbbusd",
                    "symbol": "bnbbusd",
                    "exchange": "Binance",
                },
                "btcbusd": {
                    "tick": 0.01,
                    "pair": ["BTC", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686219, tzinfo=timezone.utc
                    ),
                    "system_symbol": "btcbusd",
                    "symbol": "btcbusd",
                    "exchange": "Binance",
                },
                "xrpbusd": {
                    "tick": 1e-05,
                    "pair": ["XRP", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686458, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xrpbusd",
                    "symbol": "xrpbusd",
                    "exchange": "Binance",
                },
                "ethbusd": {
                    "tick": 0.01,
                    "pair": ["ETH", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686285, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ethbusd",
                    "symbol": "ethbusd",
                    "exchange": "Binance",
                },
                "ltcbusd": {
                    "tick": 0.01,
                    "pair": ["LTC", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686344, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ltcbusd",
                    "symbol": "ltcbusd",
                    "exchange": "Binance",
                },
                "trxbusd": {
                    "tick": 1e-05,
                    "pair": ["TRX", "BUSD"],
                    "schema": cfg.BINANCE_SPOT_SCHEMA,
                    "symbol_schema": cfg.BINANCE_SPOT_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 686401, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trxbusd",
                    "symbol": "trxbusd",
                    "exchange": "Binance",
                },
            },
        },
    },
    f"wallet.{cfg.BINANCE_ACCOUNT_NAME}": {
        "app_prefix": 1606230664,
        "exchange": {
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
    },
    "currency": {
        cfg.BINANCE_WSS_API_NAME: {cfg.BINANCE_SPOT_SCHEMA: {"btcusdt": 19124.03}},
    },
}
