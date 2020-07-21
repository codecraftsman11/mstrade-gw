from .rest import BinanceRestApi
from .wss import BinanceWssApi, BinanceFuturesWssApi


def get_connector_class(**kwargs):
    return BinanceRestApi


def get_rest_api_class(**kwargs):
    return BinanceRestApi


def get_ws_api_class(**kwargs):
    schema = kwargs.get('schema', '').lower()
    if schema == 'futures':
        return BinanceFuturesWssApi
    return BinanceWssApi
