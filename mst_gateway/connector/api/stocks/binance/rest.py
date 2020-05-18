from datetime import datetime
from bravado.exception import HTTPError
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from . import utils, var
from ...rest import StockRestApi
from .....exceptions import ConnectorError


class BinanceRestApi(StockRestApi):

    def _connect(self, **kwargs):
        return Client(api_key=self._auth['api_key'],
                      api_secret=self._auth['api_secret'])

    def ping(self) -> bool:
        try:
            self._binance_api(self._handler.ping)
        except ConnectorError:
            return False
        return True

    def get_user(self) -> dict:
        data = self._binance_api(self._handler.get_deposit_address, asset='eth')
        return utils.load_user_data(data)

    def get_symbol(self, symbol) -> dict:
        data = self._binance_api(self._handler.get_ticker, symbol=symbol.upper())
        return utils.load_symbol_data(data)

    def list_symbols(self, **kwargs) -> list:
        data = self._binance_api(self._handler.get_ticker)
        return [utils.load_symbol_data(d) for d in data if utils.to_float(d['weightedAvgPrice'])]

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol.upper(), limit=1)
        return utils.load_quote_data(data[0], symbol)

    def list_quotes(self, symbol: str, timeframe: str = None, **kwargs) -> list:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol.upper())
        return [utils.load_quote_data(d, symbol) for d in data]

    def _list_quote_bins_page(self, symbol, binsize='1m', count=100, **kwargs):
        data = self._binance_api(
            self._handler.get_klines, symbol=symbol.upper(), interval=binsize, limit=count, **kwargs
        )
        return [utils.load_quote_bin_data(d, symbol.upper()) for d in data]

    def list_quote_bins(self, symbol, binsize='1m', count=100, **kwargs) -> list:
        pages = int((count - 1) / var.BINANCE_MAX_QUOTE_BINS_COUNT + 1)
        rest = count % var.BINANCE_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        kwargs = self._api_kwargs(kwargs)
        for i in range(pages):
            if i == pages - 1:
                items_count = rest
            else:
                items_count = var.BINANCE_MAX_QUOTE_BINS_COUNT
            quotes = self._list_quote_bins_page(symbol=symbol,
                                                binsize=binsize,
                                                count=items_count,
                                                **kwargs)
            kwargs['startTime'] = quotes[-1].get('timestamp')+1
            quote_bins += quotes
        return quote_bins

    def create_order(self, symbol: str,
                     side: str = Client.SIDE_BUY,
                     value: float = 1,
                     order_type: str = Client.ORDER_TYPE_MARKET,
                     **params) -> bool:
        params.update(
            dict(
                symbol=symbol.upper(),
                side=side,
                type=order_type,
                quantity=value
            )
        )
        if params.get('order_id'):
            params['newClientOrderId'] = params.get('order_id')
        data = self._binance_api(self._handler.create_order, **params)
        return bool(data)

    def cancel_all_orders(self):
        open_orders = [dict(symbol=order["symbol"], orderId=order["orderId"]) for order in
                       self._binance_api(self._handler.get_open_orders)]
        data = [self._binance_api(self._handler.cancel_order, **order) for order in open_orders]
        return bool(data)

    def cancel_order(self, **params):
        data = self._binance_api(self._handler.cancel_order, **params)
        return bool(data)

    def get_order(self, order_id: str, **params):
        params.update(orderId=order_id)
        data = self._binance_api(self._handler.get_order, **params)
        if not data:
            return None
        return utils.load_order_data(data)

    def list_orders(self, symbol: str,
                    active_only: bool = True,
                    count: int = None,
                    offset: int = 0,
                    params: dict = None) -> list:
        if params is None:
            params = {}
        if active_only:
            data = self._binance_api(self._handler.get_open_orders, **params)
            return [utils.load_order_data(d) for d in data]
        if count is not None:
            params['limit'] = count
        data = self._binance_api(self._handler.get_all_orders, **params)
        return [utils.load_order_data(d) for d in data][offset:count]

    def list_trades(self, symbol, **params) -> list:
        data = self._binance_api(self._handler.get_recent_trades, symbol=symbol.upper(), **self._api_kwargs(params))
        return [utils.load_trade_data(d, symbol.upper()) for d in data]

    def close_order(self, order_id):
        return NotImplementedError

    def close_all_orders(self, symbol: str):
        return NotImplementedError

    def calc_face_price(self, symbol: str, price: float):
        raise NotImplementedError

    def calc_price(self, symbol: str, face_price: float):
        raise NotImplementedError

    def get_order_book(
            self, symbol: str, depth: int = None, side: int = None,
            split: bool = False, offset: int = 0):
        raise NotImplementedError

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', '').lower()
        if schema == 'exchange':
            return self._spot_wallet(**kwargs)
        if schema == 'margin2':
            return self._margin_wallet(**kwargs)
        if schema == 'futures':
            return self._futures_wallet(**kwargs)
        return dict()

    def _spot_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_account, **kwargs)
        return utils.load_spot_wallet_data(data)

    def _margin_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_margin_account, **kwargs)
        return utils.load_margin_wallet_data(data)

    def _futures_wallet(self, **kwargs):
        data = self._binance_api(self._handler.futures_account, **kwargs)
        return utils.load_futures_wallet_data(data)

    def _binance_api(self, method: callable, **kwargs):
        try:
            resp = method(**kwargs)
        except HTTPError as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.status_code}, {exc.message}")
        except BinanceAPIException as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.code}, {exc.message}")
        except BinanceRequestException as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.message}")
        if isinstance(resp, dict) and resp.get('msg'):
            try:
                _, msg = resp['msg'].split('=', 1)
            except ValueError:
                msg = resp['msg']
            raise ConnectorError(f"Binance api error. Details: {msg}")
        return resp

    def _api_kwargs(self, kwargs):
        api_kwargs = dict()
        for _k, _v in kwargs.items():
            if _k == 'date_from' and isinstance(_v, datetime):
                api_kwargs['startTime'] = int(_v.timestamp()*1000)
            if _k == 'date_to' and isinstance(_v, datetime):
                api_kwargs['endTime'] = int(_v.timestamp()*1000)
            if _k == 'count':
                api_kwargs['limit'] = _v
        return api_kwargs

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
