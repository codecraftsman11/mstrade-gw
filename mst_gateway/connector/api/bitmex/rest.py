import bitmex
from bravado.exception import HTTPError
from . import var
from ... import api
from ..rest import StockRestApi
from ....exceptions import ConnectorError
from ....utils import _j


def _bitmex_api(method: callable, **kwargs):
    try:
        resp = method(**kwargs).response()
        return resp.result, resp.metadata
    except HTTPError as exc:
        raise ConnectorError("Bitmex api error. Details: "
                             "{}, {}".format(exc.status_code, exc.message))


def store_order_type(order_type: int) -> str:
    return var.ORDER_TYPE_WRITE_MAP.get(order_type)


def load_order_type(order_type: str) -> int:
    return var.ORDER_TYPE_READ_MAP.get(order_type)


def store_order_side(order_side: int) -> str:
    if order_side == api.SELL:
        return 'Sell'
    return 'Buy'


def load_order_side(order_side: str) -> int:
    if order_side == 'Sell':
        return api.SELL
    return api.BUY


def load_order_data(raw_data: dict) -> dict:
    return {
        'symbol': raw_data['symbol'],
        'value': raw_data['orderQty'],
        'stop': raw_data['stopPx'],
        'type': load_order_type(raw_data['ordType']),
        'side': load_order_side(raw_data['side']),
        'price': raw_data['price'],
        'created': raw_data['timestamp'],
        'active': raw_data['ordStatus'] != "New"
    }


def load_symbol_data(raw_data: dict) -> dict:
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'price': raw_data.get('midPrice'),
    }


def load_quote_data(raw_data: dict) -> dict:
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'price': raw_data.get('price'),
        'volume': raw_data.get('grossValue'),
        'side': load_order_side(raw_data.get('side'))
    }


def load_quote_bin_data(raw_data: dict) -> dict:
    return {
        'timestamp': raw_data.get('timestamp'),
        'symbol': raw_data.get('symbol'),
        'open': raw_data.get("open"),
        'close': raw_data.get("close"),
        'high': raw_data.get("high"),
        'low': raw_data.get('low'),
        'volume': raw_data.get('volume'),
    }


def _make_create_order_args(args, options):
    if not isinstance(options, dict):
        return False
    if 'display_value' in options:
        args['dispalyQty'] = options['display_value']
    if 'stop_price' in options:
        args['stopPx'] = options['stop_price']
    if 'ttl_type' in options:
        args['timeInForce'] = options['ttl_type']
    if 'comment' in options:
        args['text'] = options['comment']
    return True


class BitmexRestApi(StockRestApi):
    BASE_URL = "https://www.bitmex.com/api/v1"
    TEST_URL = "https://testnet.bitmex.com/api/v1"

    def _connect(self, **kwargs):
        return bitmex.bitmex(test=self._url == self.__class__.TEST_URL,
                             api_key=self._auth['api_key'],
                             api_secret=self._auth['api_secret'])

    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        if timeframe is not None:
            symbol = symbol + ":" + timeframe
        quotes, _ = _bitmex_api(self._handler.Trade.Trade_get,
                                symbol=symbol.upper(),
                                reverse=True,
                                **kwargs)
        return [load_quote_data(data) for data in quotes]

    def _list_quote_bins_page(self, symbol, binsize='1m', count=100, offset=0,
                              **kwargs):
        quote_bins, _ = _bitmex_api(self._handler.Trade.Trade_getBucketed,
                                    symbol=symbol.upper(),
                                    binSize=binsize,
                                    reverse=True,
                                    count=count,
                                    start=offset,
                                    **kwargs)
        return [load_quote_bin_data(data) for data in quote_bins]

    def list_quote_bins(self, symbol, binsize='1m', count=100, **kwargs) -> list:
        pages = int((count - 1) / var.BITMEX_MAX_QUOTE_BINS_COUNT) + 1
        rest = count % var.BITMEX_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        for i in range(pages):
            if i == pages - 1:
                items_count = rest
            else:
                items_count = var.BITMEX_MAX_QUOTE_BINS_COUNT
            quotes = self._list_quote_bins_page(symbol=symbol,
                                                binsize=binsize,
                                                offset=i * var.BITMEX_MAX_QUOTE_BINS_COUNT,
                                                count=items_count,
                                                **kwargs)
            quote_bins += quotes
        return quote_bins

    def get_user(self, **kwargs) -> dict:
        data, _ = _bitmex_api(self._handler.User.User_get, **kwargs)
        return data

    def list_symbols(self, **kwargs) -> list:
        instruments, _ = _bitmex_api(self._handler.Instrument.Instrument_getActive,
                                     **kwargs)
        return [load_symbol_data(data) for data in instruments]

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        quotes, _ = _bitmex_api(self._handler.Trade.Trade_get,
                                symbol=symbol.upper(),
                                reverse=True,
                                count=1)
        return load_quote_data(quotes[0])

    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: int = api.MARKET,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        args = dict(
            symbol=symbol.upper(),
            side=store_order_side(side),
            orderQty=value,
            ordType=store_order_type(order_type)
        )
        if price is None:
            args['ordType'] = 'Market'
        else:
            args['price'] = price
        if order_id is not None:
            args['clOrdID'] = order_id
        _make_create_order_args(args, options)
        data, _ = _bitmex_api(self._handler.Order.Order_new, **args)
        return bool(data)

    def cancel_all_orders(self):
        data, _ = _bitmex_api(self._handler.Order.Order_cancelAll)
        return bool(data)

    def cancel_order(self, order_id):
        data, _ = _bitmex_api(self._handler.Order.Order_cancel,
                              orderID=order_id)
        return bool(data)

    def get_order(self, order_id: str) -> dict:
        data, _ = _bitmex_api(self._handler.Order.Order_getOrders, filter=_j({
            'clOrdID': order_id
        }))
        if not data:
            return None
        return load_order_data(data[0])

    def list_orders(self, symbol: str, active_only: bool = True, options: dict = None) -> list:
        if options is None:
            options = {}
        if active_only:
            if 'filter' not in options:
                options['filter'] = {}
            options['filter']['open'] = True
            options['filter'] = _j(options['filter'])
        orders, _ = _bitmex_api(self._handler.Order.Order_getOrders,
                                symbol=symbol.upper(),
                                **options)
        return [load_order_data(data) for data in orders]

    def close_order(self, order_id) -> bool:
        order = self.get_order(order_id)
        return self.close_all_orders(order['symbol'])

    def close_all_orders(self, symbol: str) -> bool:
        data, _ = _bitmex_api(self._handler.Order.Order_closePosition,
                              symbol=symbol.upper())
        return bool(data)
