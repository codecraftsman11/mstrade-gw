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
    f"{StateStorageKey.symbol}.bitmex.{OrderSchema.margin}": {
        'ethusd': {
            "tick": 0.05,
            "pair": [
                "ETH",
                "USD"
            ],
            "volume_tick": 1.0,
            "max_leverage": 100.0,
            "schema": "margin",
            "expiration": None,
            "expiration_date": None,
            "created": "2020-06-25T13:02:57.516637",
            "system_symbol": "ethusd",
            "symbol": "ethusd",
            "exchange": "Bitmex",
            'wallet_asset': 'XBT',
            "extra": {
                'face_price_data': {
                    'is_quanto': True,
                    'is_inverse': False,
                    'multiplier': 100,
                    'underlying_multiplier': None,
                },
                "leverage_brackets": [],
            },
        },
        'xbtusd': {
            "tick": 0.5,
            "pair": [
                "XBT",
                "USD"
            ],
            "volume_tick": 100.0,
            "max_leverage": 100.0,
            "schema": "margin",
            "expiration": None,
            "expiration_date": None,
            "created": "2020-07-01T15:10:14.834558",
            "system_symbol": "btcusd",
            "symbol": "xbtusd",
            "exchange": "Bitmex",
            'wallet_asset': 'XBT',
            "extra": {
                'face_price_data': {
                    'is_quanto': False,
                    'is_inverse': True,
                    'multiplier': -100000000,
                    'underlying_multiplier': None,
                },
                "leverage_brackets": [],
            },
        }
    },
    f"{StateStorageKey.symbol}.tbitmex.{OrderSchema.margin}": {
        'ethusd': {
            "tick": 0.05,
            "pair": [
                "ETH",
                "USD"
            ],
            "volume_tick": 1.0,
            "max_leverage": 100.0,
            "schema": "margin",
            "expiration": None,
            "expiration_date": None,
            "created": "2020-06-25T13:03:00.347559",
            "system_symbol": "ethusd",
            "symbol": "ethusd",
            "exchange": "tBitmex",
            'wallet_asset': 'XBT',
            "extra": {
                'face_price_data': {
                    'is_quanto': True,
                    'is_inverse': False,
                    'multiplier': 100,
                    'underlying_multiplier': None,
                },
                "leverage_brackets": [],
            },
        },
        'xbtusd': {
            "tick": 0.5,
            "pair": [
                "XBT",
                "USD"
            ],
            "volume_tick": 100.0,
            "max_leverage": 100.0,
            "schema": "margin",
            "expiration": None,
            "expiration_date": None,
            "created": "2020-07-01T15:10:16.748936",
            "system_symbol": "btcusd",
            "symbol": "xbtusd",
            "exchange": "tBitmex",
            'wallet_asset': 'XBT',
            "extra": {
                'face_price_data': {
                    'is_quanto': False,
                    'is_inverse': True,
                    'multiplier': -100000000,
                    'underlying_multiplier': None,
                },
                "leverage_brackets": [],
            },
        },
    }
}

WALLET_DATA = {
    OrderSchema.margin:
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
