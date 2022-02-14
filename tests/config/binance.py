from os import getenv


BINANCE_SPOT_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_SPOT_TESTNET_WSS_API_URL', 'wss://testnet.binance.vision/ws'
)
BINANCE_SPOT_TESTNET_AUTH_KEYS = {
    'api_key': 'FYU3VOwZnT3b0Y3wJTK0L4X8ufpb9OL1X8a7MsCk470Nuf41S31A9PeYLHVKLykb',
    'api_secret': 'IhDdcjgM1ZTnp6sgGSsNn1CyesDJhdQJoZdQOSZ9PvsigFqnevfiGJNTxJuWAhTh',
}
BINANCE_MARGIN_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_MARGIN_TESTNET_WSS_API_URL', 'wss://stream.binancefuture.com/ws'
)
BINANCE_MARGIN_TESTNET_AUTH_KEYS = {
    'api_key': '7689ad91e14c55e8640faa8ead26444a5fefa5e8b029c8aca66d1cc468d4f1ba',
    'api_secret': '820ee3f7ed4f06b620bf18cc1ab56b8bb450c040df3d9ec149597e51e49d5528',
}
BINANCE_MARGIN_COIN_TESTNET_WSS_API_URL = getenv(
    'GW_BINANCE_MARGIN_TESTNET_WSS_API_URL', 'wss://dstream.binancefuture.com/ws'
)
BINANCE_MARGIN_COIN_TESTNET_AUTH_KEYS = {
    'api_key': '7689ad91e14c55e8640faa8ead26444a5fefa5e8b029c8aca66d1cc468d4f1ba',
    'api_secret': '820ee3f7ed4f06b620bf18cc1ab56b8bb450c040df3d9ec149597e51e49d5528',
}
