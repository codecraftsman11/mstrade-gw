from os import getenv
from mst_gateway.connector.api.types import OrderSchema

BINANCE_ACCOUNT_NAME = "binance.binance.1"
BINANCE_WSS_API_NAME = "binance"
BINANCE_AUTH_KEYS = {
    "api_key": getenv("BINANCE_API_KEY"),
    "api_secret": getenv("BINANCE_API_SECRET"),
}

BINANCE_SPOT_TESTNET_URL = getenv(
    "BINANCE_SPOT_TESTNET_URL", "wss://testnet.binance.vision/ws"
)
BINANCE_SPOT_SCHEMA = OrderSchema.exchange
BINANCE_SPOT_TESTNET_AUTH_KEYS = {
    "api_key": getenv("BINANCE_SPOT_TESTNET_API_KEY"),
    "api_secret": getenv("BINANCE_SPOT_TESTNET_API_SECRET"),
}

BINANCE_FUTURES_TESTNET_URL = getenv(
    "BINANCE_FUTURES_TESTNET_URL", "wss://stream.binancefuture.com/ws"
)
BINANCE_FUTURES_SCHEMA = OrderSchema.futures
BINANCE_FUTURES_TESTNET_AUTH_KEYS = {
    "api_key": getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
    "api_secret": getenv("BINANCE_FUTURES_TESTNET_API_SECRET"),
}
