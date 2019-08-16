import json
import bitmex
from bravado.exception import HTTPError
from . import var
from . import utils
from ...rest import StockRestApi
from .... import api
from .....exceptions import ConnectorError
from .....utils import j_dumps


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
        self._keepalive = bool(kwargs.get('keepalive', False))
        self._compress = bool(kwargs.get('compress', False))
        return bitmex.bitmex(test=self._url == self.__class__.TEST_URL,
                             api_key=self._auth['api_key'],
                             api_secret=self._auth['api_secret'])

    def _api_kwargs(self, kwargs):
        # pylint: disable=no-self-use
        api_kwargs = dict(filter={})
        for _k, _v in kwargs.items():
            if _k == 'date_from':
                api_kwargs['startTime'] = _v
            if _k == 'date_to':
                api_kwargs['endTime'] = _v
            if _k == 'count':
                api_kwargs['count'] = _v
        if not api_kwargs['filter']:
            del api_kwargs['filter']
        else:
            api_kwargs['filter'] = json.dumps(api_kwargs['filter'])
        return api_kwargs

    def list_quotes(self, symbol, timeframe=None, **kwargs) -> list:
        if timeframe is not None:
            symbol = symbol + ":" + timeframe
        quotes, _ = self._bitmex_api(self._handler.Trade.Trade_get,
                                     symbol=symbol.upper(),
                                     reverse=True,
                                     **self._api_kwargs(kwargs))
        return [utils.load_quote_data(data) for data in quotes]

    def _list_quote_bins_page(self, symbol, binsize='1m', count=100, offset=0,
                              **kwargs):
        quote_bins, _ = self._bitmex_api(self._handler.Trade.Trade_getBucketed,
                                         symbol=symbol.upper(),
                                         binSize=binsize,
                                         reverse=True,
                                         start=offset,
                                         count=count,
                                         **self._api_kwargs(kwargs))
        return [utils.load_quote_bin_data(data) for data in quote_bins]

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
        data, _ = self._bitmex_api(self._handler.User.User_get, **kwargs)
        return data

    def list_symbols(self, **kwargs) -> list:
        instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive,
                                          **kwargs)
        return [utils.load_symbol_data(data) for data in instruments]

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        quotes, _ = self._bitmex_api(self._handler.Trade.Trade_get,
                                     symbol=symbol.upper(),
                                     reverse=True,
                                     count=1)
        return utils.load_quote_data(quotes[0])

    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: int = api.MARKET,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        args = dict(
            symbol=symbol.upper(),
            side=utils.store_order_side(side),
            orderQty=value,
            ordType=utils.store_order_type(order_type)
        )
        if price is None:
            args['ordType'] = 'Market'
        else:
            args['price'] = price
        if order_id is not None:
            args['clOrdID'] = order_id
        _make_create_order_args(args, options)
        data, _ = self._bitmex_api(self._handler.Order.Order_new, **args)
        return bool(data)

    def cancel_all_orders(self):
        data, _ = self._bitmex_api(self._handler.Order.Order_cancelAll)
        return bool(data)

    def cancel_order(self, order_id):
        data, _ = self._bitmex_api(self._handler.Order.Order_cancel,
                                   orderID=order_id)
        return bool(data)

    def get_order(self, order_id: str) -> dict:
        data, _ = self._bitmex_api(self._handler.Order.Order_getOrders,
                                   filter=j_dumps({
                                       'clOrdID': order_id
                                   }))
        if not data:
            return None
        return utils.load_order_data(data[0])

    def list_orders(self, symbol: str, active_only: bool = True,
                    count: int = None, offset: int = 0, options: dict = None) -> list:
        if options is None:
            options = {}
        if active_only:
            if 'filter' not in options:
                options['filter'] = {}
            options['filter']['open'] = True
            options['filter'] = j_dumps(options['filter'])
        if count is not None:
            options['count'] = count
        if offset > 0:
            options['start'] = offset
        orders, _ = self._bitmex_api(self._handler.Order.Order_getOrders,
                                     symbol=symbol.upper(),
                                     reverse=True,
                                     **options)
        return [utils.load_order_data(data) for data in orders]

    def close_order(self, order_id) -> bool:
        order = self.get_order(order_id)
        return self.close_all_orders(order['symbol'])

    def close_all_orders(self, symbol: str) -> bool:
        data, _ = self._bitmex_api(self._handler.Order.Order_closePosition,
                                   symbol=symbol.upper())
        return bool(data)

    def _bitmex_api(self, method: callable, **kwargs):
        headers = {}
        if self._keepalive:
            headers['Connection'] = "keep-alive"
        if self._compress:
            headers['Accept-Encoding'] = "deflate, gzip;q=1.0, *;q=0.5"
        try:
            resp = method(_request_options={'headers': headers}, **kwargs).response()
            return resp.result, resp.metadata
        except HTTPError as exc:
            raise ConnectorError("Bitmex api error. Details: "
                                 "{}, {}".format(exc.status_code, exc.message))
