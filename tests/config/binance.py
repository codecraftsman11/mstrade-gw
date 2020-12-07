from os import getenv
from mst_gateway.connector.api.types import OrderSchema

BINANCE_ACCOUNT_NAME = "binance.binance.1"
BINANCE_WSS_API_NAME = "binance.binance"
BINANCE_AUTH_KEYS = {
    "api_key": getenv("BINANCE_API_KEY"),
    "api_secret": getenv("BINANCE_API_SECRET"),
}

BINANCE_SPOT_SCHEMA = OrderSchema.exchange
BINANCE_FUTURES_SCHEMA = OrderSchema.futures
