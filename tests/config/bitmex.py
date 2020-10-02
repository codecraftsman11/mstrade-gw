from os import getenv


BITMEX_NAME = "bitmex"
BITMEX_SCHEMA = "margin1"
BITMEX_SYMBOL = "XBTUSD"
BITMEX_URL = "https://testnet.bitmex.com/api/v1"
BITMEX_WSS_URL = "wss://testnet.bitmex.com/realtime"
BITMEX_API_KEY = getenv('BITMEX_API_KEY')
BITMEX_API_SECRET = getenv('BITMEX_API_SECRET')
BITMEX_USERNAME = getenv('BITMEX_USERNAME', "belka158")
BITMEX_EMAIL = getenv('BITMEX_EMAIL', "belka158@gmail.com")
BITMEX_LOCALE = "en-US"
