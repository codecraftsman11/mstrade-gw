from .rest import BinanceRestApi


def get_rest_api_class():
    return BinanceRestApi


def get_ws_api_class():
    raise NotImplementedError
