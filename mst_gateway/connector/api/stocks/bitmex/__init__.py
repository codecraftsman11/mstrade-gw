from .rest import BitmexRestApi
from .wss import BitmexWssApi


def get_connector_class():
    return BitmexRestApi


def get_rest_api_class():
    return BitmexRestApi


def get_ws_api_class():
    return BitmexWssApi
