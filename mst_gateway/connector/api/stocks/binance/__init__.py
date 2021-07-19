from .rest import BinanceRestApi
from .wss import BinanceWssApi, BinanceFuturesWssApi, BinanceFuturesCoinWssApi
from mst_gateway.connector.api.types.order import OrderSchema


def get_connector_class(**kwargs):
    return BinanceRestApi


def get_rest_api_class(**kwargs):
    return BinanceRestApi


def get_ws_api_class(**kwargs):
    schema = kwargs.get('schema', '').lower()
    if schema == OrderSchema.futures:
        return BinanceFuturesWssApi
    if schema == OrderSchema.futures_coin:
        return BinanceFuturesCoinWssApi
    return BinanceWssApi
