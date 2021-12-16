from os import getenv


BITMEX_NAME = "bitmex"
BITMEX_SCHEMA = "margin1"
BITMEX_SYMBOL = "XBTUSD"
BITMEX_URL = "https://testnet.bitmex.com/api/v1"
BITMEX_WSS_URL = "wss://testnet.bitmex.com/realtime"
BITMEX_API_KEY = getenv('GW_BITMEX_API_KEY')
BITMEX_API_SECRET = getenv('GW_BITMEX_API_SECRET')
BITMEX_USERNAME = getenv('GW_BITMEX_USERNAME', "belka158")
BITMEX_EMAIL = getenv('GW_BITMEX_EMAIL', "belka158@gmail.com")
BITMEX_LOCALE = "en-US"
BITMEX_TESTNET_AUTH_KEYS = {
    'api_key': BITMEX_API_KEY,
    'api_secret': BITMEX_API_SECRET
}
