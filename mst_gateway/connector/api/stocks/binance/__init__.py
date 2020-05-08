from .rest import BinanceRestApi


def get_connector_class():
    raise NotImplementedError


def get_rest_api_class():
    return BinanceRestApi


def get_ws_api_class():
    raise NotImplementedError
