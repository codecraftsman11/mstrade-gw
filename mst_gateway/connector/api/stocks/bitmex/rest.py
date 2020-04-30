import json
from typing import (
    Tuple,
    Optional,
    Union,
    List
)
from bravado.exception import HTTPError
from .bitmex import bitmex_connector, APIKeyAuthenticator
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


class BitmexFactory:
    BASE_URL = "https://www.bitmex.com/api/v1"
    TEST_URL = "https://testnet.bitmex.com/api/v1"
    BITMEX_SWAGGER = bitmex_connector(test=False)
    TBITMEX_SWAGGER = bitmex_connector(test=True)

    @classmethod
    def make_client(cls, url):
        if url == cls.BASE_URL:
            swagger = cls.BITMEX_SWAGGER
        else:
            swagger = cls.TBITMEX_SWAGGER
        return swagger


class BitmexRestApi(StockRestApi):
    BASE_URL = BitmexFactory.BASE_URL
    TEST_URL = BitmexFactory.TEST_URL

    def _connect(self, **kwargs):
        self._keepalive = bool(kwargs.get('keepalive', False))
        self._compress = bool(kwargs.get('compress', False))
        return BitmexFactory.make_client(self._url)

    @property
    def _authenticator(self):
        self._auth = self._auth if isinstance(self._auth, dict) else {}
        return APIKeyAuthenticator(
            host=self._url,
            api_key=self._auth.get('api_key'),
            api_secret=self._auth.get('api_secret')
        )

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

    def list_wallets(self, **kwargs) -> List[dict]:
        data, _ = self._bitmex_api(self._handler.User.User_getMargin, **kwargs)
        return [{'margin1': utils.load_wallet_data(data)}]

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

    def get_order_book(
            self, symbol: str, depth: int = None, side: int = None,
            split: bool = False, offset: int = 0) -> Union[list, dict]:
        ob_depth = depth or 0
        if ob_depth:
            ob_depth += offset
        ob_items, _ = self._bitmex_api(self._handler.OrderBook.OrderBook_getL2,
                                       symbol=utils.symbol2stock(symbol),
                                       depth=ob_depth)
        if not split \
           and side is None \
           and not offset:
            return [utils.load_order_book_data(_ob)
                    for _ob in ob_items]

        splitted_ob = utils.split_order_book(
            ob_items,
            utils.store_order_side(side),
            offset
        )
        if split:
            return splitted_ob
        if side is None:
            return splitted_ob.get(api.SELL, []) \
                + splitted_ob.get(api.BUY, [])
        return splitted_ob.get(side, [])

    def _bitmex_api(self, method: callable, **kwargs):
        headers = {}
        if self._keepalive:
            headers['Connection'] = "keep-alive"
        if self._compress:
            headers['Accept-Encoding'] = "deflate, gzip;q=1.0, *;q=0.5"
        try:
            resp = method(
                authenticator=self._authenticator,
                _request_options={'headers': headers},
                **kwargs
            ).response()
            return resp.result, resp.metadata
        except HTTPError as exc:
            message = exc.swagger_result.get('error', {}).get('message') \
                if isinstance(exc.swagger_result, dict) \
                else ''
            raise ConnectorError(f"Bitmex api error. Details: {exc.status_code}, {exc.message or message}")

    @classmethod
    def calc_face_price(cls, symbol: str, price: float) -> Tuple[Optional[float],
                                                                 Optional[bool]]:
        return utils.calc_face_price(symbol, price)

    @classmethod
    def calc_price(cls, symbol: str, face_price: float) -> Optional[float]:
        return utils.calc_price(symbol, face_price)

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
