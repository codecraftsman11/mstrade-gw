import bitmex
from bravado.exception import HTTPError
from ..base import StockApi
from ....exceptions import ConnectorError
from ....connector import api
from ....utils import j_q


ORDER_TYPE_WRITE_MAP = {
    api.MARKET: 'Market',
    api.LIMIT: 'Limit',
    api.STOP: 'Stop'
}


ORDER_TYPE_READ_MAP = {
    v: k for k, v in ORDER_TYPE_WRITE_MAP
}


def _bitmex_api(method: callable, **kwargs):
    try:
        return method(**kwargs).result()
    except HTTPError as exc:
        raise ConnectorError("Bitmex api error. Details: " + exc)


def store_order_type(order_type: int) -> str:
    return ORDER_TYPE_WRITE_MAP.get(order_type)


def load_order_type(order_type: str) -> int:
    return ORDER_TYPE_READ_MAP.get(order_type)


class BitmexRestApi(StockApi):
    BASE_URL = "https://www.bitmex.com/api/v1"
    TEST_URL = "https://testnet.bitmex.com/api/v1"

    def _connect(self, **kwargs):
        return bitmex.bitmex(test=self._url == self.__class__.TEST_URL,
                             api_key=self._auth['api_key'],
                             api_secret=self._auth['api_secret'])

    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        if timeframe is not None:
            symbol = symbol + ":" + timeframe
        body, _ = _bitmex_api(self._handler.Trade.Trade_get,
                              symbol=symbol,
                              reverse=True,
                              **kwargs)[0]
        return body

    def get_user(self, **kwargs) -> dict:
        return _bitmex_api(self._handler.User.User_get, **kwargs)

    def list_symbols(self, **kwargs) -> dict:
        body, _ = _bitmex_api(self._handler.Instrument.Instrument_getActive,
                              **kwargs)
        return [{
            'symbol': data.get('symbol'),
            'type': data.get('typ'),
            'state': data.get('stat')
        } for data in j_q(body)]

    def create_order(self, symbol: str, order_type: int, rate: float,
                     quantity: float, options: dict = None) -> bool:
        _bitmex_api(self._handler.Order.Order_post,
                    symbol=symbol,
                    ordType=store_order_type(order_type),
                    ordQty=quantity,
                    price=rate)
