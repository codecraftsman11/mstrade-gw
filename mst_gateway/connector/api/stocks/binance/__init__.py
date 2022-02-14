from .rest import BinanceRestApi
from .wss import BinanceWssApi, BinanceMarginWssApi, BinanceMarginCoinWssApi
from mst_gateway.connector.api.types.order import OrderSchema


def get_connector_class(**kwargs):
    return BinanceRestApi


def get_rest_api_class(**kwargs):
    return BinanceRestApi


def get_ws_api_class(**kwargs):
    schema = kwargs.get('schema', '').lower()
    if schema == OrderSchema.margin:
        return BinanceMarginWssApi
    if schema == OrderSchema.margin_coin:
        return BinanceMarginCoinWssApi
    return BinanceWssApi
