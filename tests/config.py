from os import getenv


BITMEX_URL = "https://testnet.bitmex.com/api/v1"
BITMEX_SYMBOL = "XBTUSD"
BITMEX_API_KEY = getenv('BITMEX_API_KEY')
BITMEX_API_SECRET = getenv('BITMEX_API_SECRET')
BITMEX_USERNAME = "belka158@gmail.com"
BITMEX_EMAIL = "belka158@gmail.com"
BITMEX_LOCALE = "en-US"


SYMBOL_FIELDS = (
    'timestamp',
    'symbol',
    'price'
)

QUOTE_FIELDS = (
    "timestamp",
    "symbol",
    "volume",
    "price",
    "side",
)

QUOTE_BIN_FIELDS = (
    "timestamp",
    "symbol",
    "volume",
    "open",
    "high",
    "low",
    "close",
)

ORDER_FIELDS = (
    'symbol',
    'value',
    'stop',
    'type',
    'side',
    'price',
    'created',
    'active'
)
