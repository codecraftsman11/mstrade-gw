from .rest import BinanceRestApi
from .wss import BinanceWssApi


def get_connector_class():
    return BinanceRestApi


def get_rest_api_class():
    return BinanceRestApi


def get_ws_api_class():
    return BinanceWssApi
