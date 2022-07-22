from os import getenv


BINANCE_SPOT_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_SPOT_TESTNET_WSS_API_URL', 'wss://testnet.binance.vision/ws'
)
BINANCE_SPOT_TESTNET_AUTH_KEYS = {
    'api_key': "pr8BQeAPhqT1Zri3jjRYtLL8HdGFqLg3YzIIvwZbstZmNiB039MoA0aiwokC07Lu",
    'api_secret': "xvP54aYi2kRY16CVhgsfT7uZ3HCFqrdG64gBXugXfFKLOoFNB2FlYcNYKKWh11XZ",
}
BINANCE_MARGIN_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_MARGIN_TESTNET_WSS_API_URL', 'wss://stream.binancefuture.com/ws'
)
BINANCE_FUTURES_TESTNET_AUTH_KEYS = {
    'api_key': "bbf39a048442bed04580f249750312dfc84e3e3bd46aacfcaf7bed5437e0ec3a",
    'api_secret': "c164aad9796feb7f1737fa75a41df5ee6694ea7aa4f8460715fd51a1f4c3b1e2",
}
BINANCE_FUTURES_COIN_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_FUTURES_COIN_TESTNET_WSS_API_URL', 'wss://dstream.binancefuture.com/ws'
)
BINANCE_FUTURES_COIN_TESTNET_AUTH_KEYS = {
    'api_key': "bbf39a048442bed04580f249750312dfc84e3e3bd46aacfcaf7bed5437e0ec3a",
    'api_secret': "c164aad9796feb7f1737fa75a41df5ee6694ea7aa4f8460715fd51a1f4c3b1e2",
}
