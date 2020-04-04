from typing import Optional
import json
import bitmex
from bravado.exception import HTTPError
from bravado.client import SwaggerClient
from BitMEXAPIKeyAuthenticator import APIKeyAuthenticator
from . import utils, var
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


class BitmexFactory():
    BASE_URL = "https://www.bitmex.com/api/v1"
    TEST_URL = "https://testnet.bitmex.com/api/v1"
    BITMEX_SWAGGER = bitmex.bitmex(test=False)
    TBITMEX_SWAGGER = bitmex.bitmex(test=True)

    @classmethod
    def make_client(cls, url, api_key, api_secret):
        swagger = cls._get_swagger_spec(url)
        if api_key and api_secret:
            swagger.swagger_spec.http_client.authenticator = APIKeyAuthenticator(
                host=url,
                api_key=api_key,
                api_secret=api_secret,
            )
        return swagger

    @classmethod
    def _get_swagger_spec(cls, url):
        if url == cls.BASE_URL:
            swagger = cls.BITMEX_SWAGGER
        else:
            swagger = cls.TBITMEX_SWAGGER
        return SwaggerClient.from_spec(
            spec_dict=swagger.swagger_spec.client_spec_dict,
            origin_url=swagger.swagger_spec.origin_url,
            config=swagger.swagger_spec.config)


class BitmexRestApi(StockRestApi):

    def _connect(self, **kwargs):
        self._keepalive = bool(kwargs.get('keepalive', False))
        self._compress = bool(kwargs.get('compress', False))
        return BitmexFactory.make_client(
            self._url,
            self._auth.get('api_key'),
            self._auth.get('api_secret'))

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
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     **self._api_kwargs(kwargs))
        return [utils.load_quote_data(data) for data in quotes]

    def _list_quote_bins_page(self, symbol, binsize='1m', count=100, offset=0,
                              **kwargs):
        quote_bins, _ = self._bitmex_api(self._handler.Trade.Trade_getBucketed,
                                         symbol=utils.symbol2stock(symbol),
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

    def get_symbol(self, symbol) -> dict:
        instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_get,
                                          symbol=utils.symbol2stock(symbol))
        if not instruments:
            return dict()
        return utils.load_symbol_data(instruments[0])

    def list_symbols(self, **kwargs) -> list:
        instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive,
                                          **kwargs)
        return [utils.load_symbol_data(data) for data in instruments]

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        quotes, _ = self._bitmex_api(self._handler.Trade.Trade_get,
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     count=1)
        return utils.load_quote_data(quotes[0])

    def create_order(self, symbol: str,
                     side: int,
                     value: float = 1,
                     order_type: str = api.OrderType.market,
                     price: float = None,
                     order_id: str = None,
                     options: dict = None) -> bool:
        args = dict(
            symbol=utils.symbol2stock(symbol),
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

    def get_order(self, order_id: str) -> Optional[dict]:
        data, _ = self._bitmex_api(self._handler.Order.Order_getOrders,
                                   filter=j_dumps({
                                       'clOrdID': order_id
                                   }))
        if not data:
            return None
        return utils.load_order_data(data[0])

    def list_orders(self, symbol: str,
                    active_only: bool = True,
                    count: int = None,
                    offset: int = 0,
                    options: dict = None) -> list:
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
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     **options)
        return [utils.load_order_data(data) for data in orders]

    def list_trades(self, symbol, **kwargs) -> list:
        trades, _ = self._bitmex_api(self._handler.Trade.Trade_get,
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     **self._api_kwargs(kwargs))
        return [utils.load_trade_data(data) for data in trades]

    def close_order(self, order_id) -> bool:
        order = self.get_order(order_id)
        return self.close_all_orders(order['symbol'])

    def close_all_orders(self, symbol: str) -> bool:
        data, _ = self._bitmex_api(self._handler.Order.Order_closePosition,
                                   symbol=utils.symbol2stock(symbol))
        return bool(data)

    def _do_list_order_book(self, symbol: str,
                            depth: int = None, side: int = None) -> list:
        ob_depth = depth or 0
        ob_items, _ = self._bitmex_api(self._handler.OrderBook.OrderBook_getL2,
                                       symbol=utils.symbol2stock(symbol),
                                       depth=ob_depth)
        if side is None:
            return [utils.load_order_book_data(data) for data in ob_items]
        _side = utils.store_order_side(side)
        return [utils.load_order_book_data(data)
                for data in ob_items if data['side'] == _side]

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

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
