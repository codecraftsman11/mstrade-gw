from os import getenv
from mst_gateway.connector.api.types import OrderSchema

BINANCE_ACCOUNT_NAME = "binance.binance"
BINANCE_ACCOUNT_ID = "1"
BINANCE_SPOT_SCHEMA = OrderSchema.exchange
BINANCE_FUTURES_SCHEMA = OrderSchema.futures
BINANCE_WSS_API_ACCOUNT_NAME = f"{BINANCE_ACCOUNT_NAME}.{BINANCE_ACCOUNT_ID}"
BINANCE_WSS_API_NAME = "binance"
BINANCE_WSS_API_URL = getenv(
    "BINANCE_WSS_API_URL", "wss://stream.binance.com:9443/ws"
)
BINANCE_AUTH_KEYS = {
    "api_key": getenv("BINANCE_API_KEY"),
    "api_secret": getenv("BINANCE_API_SECRET"),
}
BINANCE_TESTNET_WSS_API_URL = getenv(
    "BINANCE_TESTNET_WSS_API_URL", "wss://testnet.binance.vision/ws"
)
BINANCE_TESTNET_AUTH_KEYS = {
    "api_key": getenv("BINANCE_TESTNET_API_KEY"),
    "api_secret": getenv("BINANCE_TESTNET_API_SECRET"),
}
