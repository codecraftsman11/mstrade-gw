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
            cfg.BINANCE_FUTURES_SCHEMA: {
                "btcusdt": {
                    "tick": 0.01,
                    "pair": ["BTC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687353, tzinfo=timezone.utc
                    ),
                    "system_symbol": "btcusd",
                    "symbol": "btcusdt",
                    "exchange": "tBinance",
                },
                "ethusdt": {
                    "tick": 0.01,
                    "pair": ["ETH", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687408, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ethusd",
                    "symbol": "ethusdt",
                    "exchange": "tBinance",
                },
                "bnbusdt": {
                    "tick": 0.001,
                    "pair": ["BNB", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688187, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bnbusd",
                    "symbol": "bnbusdt",
                    "exchange": "tBinance",
                },
                "neousdt": {
                    "tick": 0.001,
                    "pair": ["NEO", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688524, tzinfo=timezone.utc
                    ),
                    "system_symbol": "neousd",
                    "symbol": "neousdt",
                    "exchange": "tBinance",
                },
                "ltcusdt": {
                    "tick": 0.01,
                    "pair": ["LTC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687626, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ltcusd",
                    "symbol": "ltcusdt",
                    "exchange": "tBinance",
                },
                "qtumusdt": {
                    "tick": 0.001,
                    "pair": ["QTUM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688570, tzinfo=timezone.utc
                    ),
                    "system_symbol": "qtumusd",
                    "symbol": "qtumusdt",
                    "exchange": "tBinance",
                },
                "adausdt": {
                    "tick": 1e-05,
                    "pair": ["ADA", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687897, tzinfo=timezone.utc
                    ),
                    "system_symbol": "adausd",
                    "symbol": "adausdt",
                    "exchange": "tBinance",
                },
                "xrpusdt": {
                    "tick": 0.0001,
                    "pair": ["XRP", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687518, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xrpusd",
                    "symbol": "xrpusdt",
                    "exchange": "tBinance",
                },
                "eosusdt": {
                    "tick": 0.001,
                    "pair": ["EOS", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687572, tzinfo=timezone.utc
                    ),
                    "system_symbol": "eosusd",
                    "symbol": "eosusdt",
                    "exchange": "tBinance",
                },
                "iotausdt": {
                    "tick": 0.0001,
                    "pair": ["IOTA", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688351, tzinfo=timezone.utc
                    ),
                    "system_symbol": "iotausd",
                    "symbol": "iotausdt",
                    "exchange": "tBinance",
                },
                "xlmusdt": {
                    "tick": 1e-05,
                    "pair": ["XLM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687843, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xlmusd",
                    "symbol": "xlmusdt",
                    "exchange": "tBinance",
                },
                "ontusdt": {
                    "tick": 0.0001,
                    "pair": ["ONT", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688296, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ontusd",
                    "symbol": "ontusdt",
                    "exchange": "tBinance",
                },
                "trxusdt": {
                    "tick": 1e-05,
                    "pair": ["TRX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687681, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trxusd",
                    "symbol": "trxusdt",
                    "exchange": "tBinance",
                },
                "etcusdt": {
                    "tick": 0.001,
                    "pair": ["ETC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687735, tzinfo=timezone.utc
                    ),
                    "system_symbol": "etcusd",
                    "symbol": "etcusdt",
                    "exchange": "tBinance",
                },
                "icxusdt": {
                    "tick": 0.0001,
                    "pair": ["ICX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689995, tzinfo=timezone.utc
                    ),
                    "system_symbol": "icxusd",
                    "symbol": "icxusdt",
                    "exchange": "tBinance",
                },
                "vetusdt": {
                    "tick": 1e-06,
                    "pair": ["VET", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688461, tzinfo=timezone.utc
                    ),
                    "system_symbol": "vetusd",
                    "symbol": "vetusdt",
                    "exchange": "tBinance",
                },
                "linkusdt": {
                    "tick": 0.001,
                    "pair": ["LINK", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687789, tzinfo=timezone.utc
                    ),
                    "system_symbol": "linkusd",
                    "symbol": "linkusdt",
                    "exchange": "tBinance",
                },
                "wavesusdt": {
                    "tick": 0.0001,
                    "pair": ["WAVES", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689254, tzinfo=timezone.utc
                    ),
                    "system_symbol": "wavesusd",
                    "symbol": "wavesusdt",
                    "exchange": "tBinance",
                },
                "zilusdt": {
                    "tick": 1e-05,
                    "pair": ["ZIL", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688753, tzinfo=timezone.utc
                    ),
                    "system_symbol": "zilusd",
                    "symbol": "zilusdt",
                    "exchange": "tBinance",
                },
                "zrxusdt": {
                    "tick": 0.0001,
                    "pair": ["ZRX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688845, tzinfo=timezone.utc
                    ),
                    "system_symbol": "zrxusd",
                    "symbol": "zrxusdt",
                    "exchange": "tBinance",
                },
                "batusdt": {
                    "tick": 0.0001,
                    "pair": ["BAT", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688406, tzinfo=timezone.utc
                    ),
                    "system_symbol": "batusd",
                    "symbol": "batusdt",
                    "exchange": "tBinance",
                },
                "xmrusdt": {
                    "tick": 0.01,
                    "pair": ["XMR", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687952, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xmrusd",
                    "symbol": "xmrusdt",
                    "exchange": "tBinance",
                },
                "zecusdt": {
                    "tick": 0.01,
                    "pair": ["ZEC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688060, tzinfo=timezone.utc
                    ),
                    "system_symbol": "zecusd",
                    "symbol": "zecusdt",
                    "exchange": "tBinance",
                },
                "iostusdt": {
                    "tick": 1e-06,
                    "pair": ["IOST", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688616, tzinfo=timezone.utc
                    ),
                    "system_symbol": "iostusd",
                    "symbol": "iostusdt",
                    "exchange": "tBinance",
                },
                "dashusdt": {
                    "tick": 0.01,
                    "pair": ["DASH", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688006, tzinfo=timezone.utc
                    ),
                    "system_symbol": "dashusd",
                    "symbol": "dashusdt",
                    "exchange": "tBinance",
                },
                "omgusdt": {
                    "tick": 0.0001,
                    "pair": ["OMG", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688936, tzinfo=timezone.utc
                    ),
                    "system_symbol": "omgusd",
                    "symbol": "omgusdt",
                    "exchange": "tBinance",
                },
                "thetausdt": {
                    "tick": 0.0001,
                    "pair": ["THETA", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688661, tzinfo=timezone.utc
                    ),
                    "system_symbol": "thetausd",
                    "symbol": "thetausdt",
                    "exchange": "tBinance",
                },
                "enjusdt": {
                    "tick": 1e-05,
                    "pair": ["ENJ", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690365, tzinfo=timezone.utc
                    ),
                    "system_symbol": "enjusd",
                    "symbol": "enjusdt",
                    "exchange": "tBinance",
                },
                "maticusdt": {
                    "tick": 1e-05,
                    "pair": ["MATIC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 22, 14, 24, 57, 982922, tzinfo=timezone.utc
                    ),
                    "system_symbol": "maticusd",
                    "symbol": "maticusdt",
                    "exchange": "tBinance",
                },
                "atomusdt": {
                    "tick": 0.001,
                    "pair": ["ATOM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688241, tzinfo=timezone.utc
                    ),
                    "system_symbol": "atomusd",
                    "symbol": "atomusdt",
                    "exchange": "tBinance",
                },
                "ftmusdt": {
                    "tick": 1e-06,
                    "pair": ["FTM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690261, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ftmusd",
                    "symbol": "ftmusdt",
                    "exchange": "tBinance",
                },
                "algousdt": {
                    "tick": 0.0001,
                    "pair": ["ALGO", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688707, tzinfo=timezone.utc
                    ),
                    "system_symbol": "algousd",
                    "symbol": "algousdt",
                    "exchange": "tBinance",
                },
                "dogeusdt": {
                    "tick": 1e-06,
                    "pair": ["DOGE", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688982, tzinfo=timezone.utc
                    ),
                    "system_symbol": "dogeusd",
                    "symbol": "dogeusdt",
                    "exchange": "tBinance",
                },
                "tomousdt": {
                    "tick": 0.0001,
                    "pair": ["TOMO", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 13, 9, 59, 48, 898014, tzinfo=timezone.utc
                    ),
                    "system_symbol": "tomousd",
                    "symbol": "tomousdt",
                    "exchange": "tBinance",
                },
                "cvcusdt": {
                    "tick": 1e-05,
                    "pair": ["CVC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 11, 11, 8, 41, 47, 650341, tzinfo=timezone.utc
                    ),
                    "system_symbol": "cvcusd",
                    "symbol": "cvcusdt",
                    "exchange": "tBinance",
                },
                "bandusdt": {
                    "tick": 0.0001,
                    "pair": ["BAND", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689163, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bandusd",
                    "symbol": "bandusdt",
                    "exchange": "tBinance",
                },
                "xtzusdt": {
                    "tick": 0.001,
                    "pair": ["XTZ", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688127, tzinfo=timezone.utc
                    ),
                    "system_symbol": "xtzusd",
                    "symbol": "xtzusdt",
                    "exchange": "tBinance",
                },
                "renusdt": {
                    "tick": 1e-05,
                    "pair": ["REN", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 13, 9, 59, 48, 898113, tzinfo=timezone.utc
                    ),
                    "system_symbol": "renusd",
                    "symbol": "renusdt",
                    "exchange": "tBinance",
                },
                "kavausdt": {
                    "tick": 0.0001,
                    "pair": ["KAVA", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689118, tzinfo=timezone.utc
                    ),
                    "system_symbol": "kavausd",
                    "symbol": "kavausdt",
                    "exchange": "tBinance",
                },
                "rlcusdt": {
                    "tick": 0.0001,
                    "pair": ["RLC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689209, tzinfo=timezone.utc
                    ),
                    "system_symbol": "rlcusd",
                    "symbol": "rlcusdt",
                    "exchange": "tBinance",
                },
                "bchusdt": {
                    "tick": 0.01,
                    "pair": ["BCH", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 687463, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bchusd",
                    "symbol": "bchusdt",
                    "exchange": "tBinance",
                },
                "solusdt": {
                    "tick": 0.0001,
                    "pair": ["SOL", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689938, tzinfo=timezone.utc
                    ),
                    "system_symbol": "solusd",
                    "symbol": "solusdt",
                    "exchange": "tBinance",
                },
                "kncusdt": {
                    "tick": 1e-05,
                    "pair": ["KNC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688799, tzinfo=timezone.utc
                    ),
                    "system_symbol": "kncusd",
                    "symbol": "kncusdt",
                    "exchange": "tBinance",
                },
                "lrcusdt": {
                    "tick": 1e-05,
                    "pair": ["LRC", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 22, 14, 24, 57, 982770, tzinfo=timezone.utc
                    ),
                    "system_symbol": "lrcusd",
                    "symbol": "lrcusdt",
                    "exchange": "tBinance",
                },
                "compusdt": {
                    "tick": 0.01,
                    "pair": ["COMP", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 688891, tzinfo=timezone.utc
                    ),
                    "system_symbol": "compusd",
                    "symbol": "compusdt",
                    "exchange": "tBinance",
                },
                "snxusdt": {
                    "tick": 0.001,
                    "pair": ["SNX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689345, tzinfo=timezone.utc
                    ),
                    "system_symbol": "snxusd",
                    "symbol": "snxusdt",
                    "exchange": "tBinance",
                },
                "sxpusdt": {
                    "tick": 0.0001,
                    "pair": ["SXP", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689027, tzinfo=timezone.utc
                    ),
                    "system_symbol": "sxpusd",
                    "symbol": "sxpusdt",
                    "exchange": "tBinance",
                },
                "mkrusdt": {
                    "tick": 0.01,
                    "pair": ["MKR", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689300, tzinfo=timezone.utc
                    ),
                    "system_symbol": "mkrusd",
                    "symbol": "mkrusdt",
                    "exchange": "tBinance",
                },
                "storjusdt": {
                    "tick": 0.0001,
                    "pair": ["STORJ", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690049, tzinfo=timezone.utc
                    ),
                    "system_symbol": "storjusd",
                    "symbol": "storjusdt",
                    "exchange": "tBinance",
                },
                "yfiusdt": {
                    "tick": 0.1,
                    "pair": ["YFI", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689482, tzinfo=timezone.utc
                    ),
                    "system_symbol": "yfiusd",
                    "symbol": "yfiusdt",
                    "exchange": "tBinance",
                },
                "balusdt": {
                    "tick": 0.001,
                    "pair": ["BAL", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689528, tzinfo=timezone.utc
                    ),
                    "system_symbol": "balusd",
                    "symbol": "balusdt",
                    "exchange": "tBinance",
                },
                "blzusdt": {
                    "tick": 1e-05,
                    "pair": ["BLZ", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690102, tzinfo=timezone.utc
                    ),
                    "system_symbol": "blzusd",
                    "symbol": "blzusdt",
                    "exchange": "tBinance",
                },
                "srmusdt": {
                    "tick": 0.0001,
                    "pair": ["SRM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689801, tzinfo=timezone.utc
                    ),
                    "system_symbol": "srmusd",
                    "symbol": "srmusdt",
                    "exchange": "tBinance",
                },
                "crvusdt": {
                    "tick": 0.001,
                    "pair": ["CRV", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689573, tzinfo=timezone.utc
                    ),
                    "system_symbol": "crvusd",
                    "symbol": "crvusdt",
                    "exchange": "tBinance",
                },
                "oceanusdt": {
                    "tick": 1e-05,
                    "pair": ["OCEAN", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 11, 2, 9, 4, 19, 953561, tzinfo=timezone.utc
                    ),
                    "system_symbol": "oceanusd",
                    "symbol": "oceanusdt",
                    "exchange": "tBinance",
                },
                "dotusdt": {
                    "tick": 0.001,
                    "pair": ["DOT", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689391, tzinfo=timezone.utc
                    ),
                    "system_symbol": "dotusd",
                    "symbol": "dotusdt",
                    "exchange": "tBinance",
                },
                "rsrusdt": {
                    "tick": 1e-06,
                    "pair": ["RSR", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 22, 14, 24, 57, 982559, tzinfo=timezone.utc
                    ),
                    "system_symbol": "rsrusd",
                    "symbol": "rsrusdt",
                    "exchange": "tBinance",
                },
                "trbusdt": {
                    "tick": 0.001,
                    "pair": ["TRB", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689618, tzinfo=timezone.utc
                    ),
                    "system_symbol": "trbusd",
                    "symbol": "trbusdt",
                    "exchange": "tBinance",
                },
                "bzrxusdt": {
                    "tick": 0.0001,
                    "pair": ["BZRX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689846, tzinfo=timezone.utc
                    ),
                    "system_symbol": "bzrxusd",
                    "symbol": "bzrxusdt",
                    "exchange": "tBinance",
                },
                "sushiusdt": {
                    "tick": 0.0001,
                    "pair": ["SUSHI", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689755, tzinfo=timezone.utc
                    ),
                    "system_symbol": "sushiusd",
                    "symbol": "sushiusdt",
                    "exchange": "tBinance",
                },
                "yfiiusdt": {
                    "tick": 0.1,
                    "pair": ["YFII", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689664, tzinfo=timezone.utc
                    ),
                    "system_symbol": "yfiiusd",
                    "symbol": "yfiiusdt",
                    "exchange": "tBinance",
                },
                "ksmusdt": {
                    "tick": 0.001,
                    "pair": ["KSM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 15, 7, 19, 3, 431309, tzinfo=timezone.utc
                    ),
                    "system_symbol": "ksmusd",
                    "symbol": "ksmusdt",
                    "exchange": "tBinance",
                },
                "egldusdt": {
                    "tick": 0.001,
                    "pair": ["EGLD", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689892, tzinfo=timezone.utc
                    ),
                    "system_symbol": "egldusd",
                    "symbol": "egldusdt",
                    "exchange": "tBinance",
                },
                "runeusdt": {
                    "tick": 0.0001,
                    "pair": ["RUNE", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689709, tzinfo=timezone.utc
                    ),
                    "system_symbol": "runeusd",
                    "symbol": "runeusdt",
                    "exchange": "tBinance",
                },
                "uniusdt": {
                    "tick": 0.0001,
                    "pair": ["UNI", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690156, tzinfo=timezone.utc
                    ),
                    "system_symbol": "uniusd",
                    "symbol": "uniusdt",
                    "exchange": "tBinance",
                },
                "avaxusdt": {
                    "tick": 0.0001,
                    "pair": ["AVAX", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690208, tzinfo=timezone.utc
                    ),
                    "system_symbol": "avaxusd",
                    "symbol": "avaxusdt",
                    "exchange": "tBinance",
                },
                "hntusdt": {
                    "tick": 0.0001,
                    "pair": ["HNT", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690313, tzinfo=timezone.utc
                    ),
                    "system_symbol": "hntusd",
                    "symbol": "hntusdt",
                    "exchange": "tBinance",
                },
                "flmusdt": {
                    "tick": 0.0001,
                    "pair": ["FLM", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 690417, tzinfo=timezone.utc
                    ),
                    "system_symbol": "flmusd",
                    "symbol": "flmusdt",
                    "exchange": "tBinance",
                },
                "defiusdt": {
                    "tick": 0.1,
                    "pair": ["DEFI", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 9, 29, 11, 24, 2, 689437, tzinfo=timezone.utc
                    ),
                    "system_symbol": "defiusd",
                    "symbol": "defiusdt",
                    "exchange": "tBinance",
                },
                "aaveusdt": {
                    "tick": 0.001,
                    "pair": ["AAVE", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 16, 12, 37, 28, 3218, tzinfo=timezone.utc
                    ),
                    "system_symbol": "aaveusd",
                    "symbol": "aaveusdt",
                    "exchange": "tBinance",
                },
                "nearusdt": {
                    "tick": 0.0001,
                    "pair": ["NEAR", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 15, 7, 19, 3, 431514, tzinfo=timezone.utc
                    ),
                    "system_symbol": "nearusd",
                    "symbol": "nearusdt",
                    "exchange": "tBinance",
                },
                "filusdt": {
                    "tick": 0.001,
                    "pair": ["FIL", "USDT"],
                    "schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "symbol_schema": cfg.BINANCE_FUTURES_SCHEMA,
                    "expiration": None,
                    "created": datetime(
                        2020, 10, 16, 12, 37, 28, 3425, tzinfo=timezone.utc
                    ),
                    "system_symbol": "filusd",
                    "symbol": "filusdt",
                    "exchange": "tBinance",
                },
            },
        },
    },
    f"wallet.{cfg.BINANCE_ACCOUNT_NAME}": {
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
