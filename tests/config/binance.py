from os import getenv

BINANCE_SPOT_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_SPOT_TESTNET_WSS_API_URL', 'wss://testnet.binance.vision/ws'
)
BINANCE_SPOT_TESTNET_AUTH_KEYS = {
    'api_key': getenv('GW_BINANCE_SPOT_TESTNET_API_KEY'),
    'api_secret': getenv('GW_BINANCE_SPOT_TESTNET_API_SECRET'),
}
BINANCE_FUTURES_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_FUTURES_TESTNET_WSS_API_URL', 'wss://stream.binancefuture.com/ws'
)
BINANCE_FUTURES_TESTNET_AUTH_KEYS = {
    'api_key': getenv('GW_BINANCE_FUTURES_TESTNET_API_KEY'),
    'api_secret': getenv('GW_BINANCE_FUTURES_TESTNET_API_SECRET'),
}
