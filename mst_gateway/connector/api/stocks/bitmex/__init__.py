from .rest import BitmexRestApi
from .wss import BitmexWssApi


def get_rest_api():
    return BitmexRestApi


def get_ws_api():
    return BitmexWssApi
