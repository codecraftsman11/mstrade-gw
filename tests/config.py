from os import getenv
from datetime import datetime
from mst_gateway.connector import api


BITMEX_URL = "https://testnet.bitmex.com/api/v1"
BITMEX_SYMBOL = "XBTUSD"
BITMEX_API_KEY = getenv('BITMEX_API_KEY')
BITMEX_API_SECRET = getenv('BITMEX_API_SECRET')
BITMEX_USERNAME = "belka158@gmail.com"
BITMEX_EMAIL = "belka158@gmail.com"
BITMEX_LOCALE = "en-US"


SYMBOL_FIELDS = {
    'timestamp': datetime,
    'symbol': str,
    'price': float
}

QUOTE_FIELDS = {
    "timestamp": datetime,
    "symbol": str,
    "volume": int,
    "price": float,
    "side": api.side_valid,
}

QUOTE_BIN_FIELDS = {
    "timestamp": datetime,
    "symbol": str,
    "volume": int,
    "open": float,
    "high": float,
    "low": float,
    "close": float,
}

ORDER_FIELDS = {
    'symbol': str,
    'value': int,
    'stop': float,
    'type': api.type_valid,
    'side': api.side_valid,
    'price': float,
    'created': datetime,
    'active': bool
}
