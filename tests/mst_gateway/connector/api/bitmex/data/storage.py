from datetime import datetime, timezone, timedelta

from mst_gateway.connector.api import OrderSchema
from mst_gateway.storage import StateStorageKey

ASSET = "XBT"
SYMBOL = "XBTUSD"
SYSTEM_SYMBOL = "btcusd"
DEFAULT_AMOUNT = 1
DEFAULT_DEPTH = 5
DEFAULT_MIN_VOLUME_SELL = 100
DEFAULT_MIN_VOLUME_BUY = 100
FROM_DATE = datetime.now(tz=timezone.utc) - timedelta(days=2)
RANGE_TO_DATE = FROM_DATE + timedelta(minutes=1)

STORAGE_DATA = {
    StateStorageKey.symbol: {
        'bitmex': {
            'margin1': {
                'ethusd': {
                    "tick": 0.05,
                    "pair": [
                        "ETH",
                        "USD"
                    ],
                    "volume_tick": 1.0,
                    "max_leverage": 100.0,
                    "schema": "margin1",
                    "expiration": None,
                    "expiration_date": None,
                    "created": "2020-06-25T13:02:57.516637",
                    "leverage_brackets": [],
                    "system_symbol": "ethusd",
                    "symbol": "ethusd",
                    "exchange": "Bitmex"
                },
                'xbtusd': {
                    "tick": 0.5,
                    "pair": [
                        "XBT",
                        "USD"
                    ],
                    "volume_tick": 100.0,
                    "max_leverage": 100.0,
                    "schema": "margin1",
                    "expiration": None,
                    "expiration_date": None,
                    "created": "2020-07-01T15:10:14.834558",
                    "leverage_brackets": [],
                    "system_symbol": "btcusd",
                    "symbol": "xbtusd",
                    "exchange": "Bitmex"
                },
            }
        },
        'tbitmex': {
            'margin1': {
                'ethusd': {
                    "tick": 0.05,
                    "pair": [
                        "ETH",
                        "USD"
                    ],
                    "volume_tick": 1.0,
                    "max_leverage": 100.0,
                    "schema": "margin1",
                    "expiration": None,
                    "expiration_date": None,
                    "created": "2020-06-25T13:03:00.347559",
                    "leverage_brackets": [],
                    "system_symbol": "ethusd",
                    "symbol": "ethusd",
                    "exchange": "tBitmex"
                },
                'xbtusd': {
                    "tick": 0.5,
                    "pair": [
                        "XBT",
                        "USD"
                    ],
                    "volume_tick": 100.0,
                    "max_leverage": 100.0,
                    "schema": "margin1",
                    "expiration": None,
                    "expiration_date": None,
                    "created": "2020-07-01T15:10:16.748936",
                    "leverage_brackets": [],
                    "system_symbol": "btcusd",
                    "symbol": "xbtusd",
                    "exchange": "tBitmex"
                },
            }
        },
    },
    StateStorageKey.exchange_rates: {
        'tbitmex': {
            OrderSchema.margin1: {
                "xbtz21": 59417,
                "xrp": 1.008,
                "usd": 1,
                "bch": 569.25,
                "sol": 221.05,
                "usdt": 1,
                "altmex": 188.86,
                "defimex": 209.27,
                "luna": 42.031,
                "avax": 133.17,
                "xbt": 58293.5,
                "xbtx21": 58404.5,
                "usdx21": 1,
                "usdz21": 1,
                "usdtz21": 1,
                "xbth22": 62134,
                "usdh22": 1,
                "eth": 4244.75,
                "ethz21": 4330.9,
                "ltc": 217.21,
                "xrpz21": 1.10159118,
                "bchz21": 592.38749,
                "adaz21": 1.88054805,
                "eosz21": 4.39864051,
                "trxz21": 0.1067604656,
                "eur": 1.125541836,
                "eurz21": 1.1273396515,
                "ltcz21": 225.487515
            }
        },
    }
}

WALLET_DATA = {
    OrderSchema.margin1:
        {
            'currency': 'XBT',
            'balance': 0.01221285,
            'withdraw_balance': 0.01218895,
            'unrealised_pnl': -5.35e-06,
            'margin_balance': 0.0122075,
            'maint_margin': 1,
            'init_margin': 0.0,
            'available_margin': 0.01218895,
            'type': 'trade'
        }
}
