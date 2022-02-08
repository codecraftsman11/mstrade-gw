from os import getenv


BITMEX_WSS_URL = getenv('GW_BITMEX_WSS_URL', 'wss://ws.testnet.bitmex.com/realtime')
BITMEX_TESTNET_AUTH_KEYS = {
    'api_key': getenv('GW_BITMEX_API_KEY'),
    'api_secret': getenv('GW_BITMEX_API_SECRET')
}
