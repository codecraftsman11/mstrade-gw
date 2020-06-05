from logging import Logger
from datetime import datetime, timedelta
from bravado.exception import HTTPError
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .lib import Client
from . import utils, var
from ...rest import StockRestApi
from ...rest.throttle import ThrottleRest
from .....exceptions import ConnectorError


class BinanceRestApi(StockRestApi):

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None,
                 throttle_storage=None, throttle_hash_name: str = '*'):
        super().__init__(url, auth, logger)
        self._throttle_hash_name = throttle_hash_name
        if throttle_storage:
            self.throttle = ThrottleRest(storage=throttle_storage)

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
        raise NotImplementedError

    def close_all_orders(self, symbol: str):
        raise NotImplementedError

    def calc_face_price(self, symbol: str, price: float):
        raise NotImplementedError

    def calc_price(self, symbol: str, face_price: float):
        raise NotImplementedError

    def get_order_book(
            self, symbol: str, depth: int = None, side: int = None,
            split: bool = False, offset: int = 0, schema: str = None):
        limit = 100
        if depth:
            for _l in [100, 500, 1000, 5000]:
                if _l >= offset+depth:
                    limit = _l
                    break
        if schema == 'futures':
            data = self._binance_api(self._handler.futures_order_book, symbol=symbol.upper(), limit=limit)
        else:
            data = self._binance_api(self._handler.get_order_book, symbol=symbol.upper(), limit=limit)
        return utils.load_order_book_data(data, symbol, side, split, offset, depth)

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', '').lower()
        if schema == 'exchange':
            return self._spot_wallet(**kwargs)
        if schema == 'margin2':
            return self._margin_wallet(**kwargs)
        if schema == 'futures':
            return self._futures_wallet(**kwargs)
        return dict(balances=list())

    def _spot_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_account, **kwargs)
        return utils.load_spot_wallet_data(data)

    def _margin_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_margin_account, **kwargs)
        return utils.load_margin_wallet_data(data)

    def _futures_wallet(self, **kwargs):
        data = self._binance_api(self._handler.futures_account, **kwargs)
        return utils.load_futures_wallet_data(data)

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        if schema.lower() == 'exchange':
            _spot = self._binance_api(self._handler.get_account, **kwargs)
            return {
                'exchange': utils.load_spot_wallet_detail_data(_spot, asset),
            }
        if schema.lower() == 'margin2':
            _spot = self._binance_api(self._handler.get_account, **kwargs)
            _margin = self._binance_api(self._handler.get_margin_account, **kwargs)
            _borrow = self._binance_api(self._handler.get_max_margin_loan, asset=asset.upper())
            return {
                'exchange': utils.load_spot_wallet_detail_data(_spot, asset),
                'margin2': utils.load_margin_wallet_detail_data(_margin, asset, _borrow)
            }
        if schema.lower() == 'futures':
            _spot = self._binance_api(self._handler.get_account, **kwargs)
            _futures = self._binance_api(self._handler.futures_account, **kwargs)
            return {
                'exchange': utils.load_spot_wallet_detail_data(_spot, asset),
                'futures': utils.load_futures_wallet_detail_data(_futures, asset)
            }
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float) -> dict:
        if from_wallet.lower() == 'exchange' and to_wallet.lower() == 'margin2':
            method = self._handler.transfer_spot_to_margin
        elif from_wallet.lower() == 'margin2' and to_wallet.lower() == 'exchange':
            method = self._handler.transfer_margin_to_spot
        elif from_wallet.lower() == 'exchange' and to_wallet.lower() == 'futures':
            method = self._handler.futures_transfer_spot_to_futures
        elif from_wallet.lower() == 'futures' and to_wallet.lower() == 'exchange':
            method = self._handler.futures_transfer_futures_to_spot
        else:
            raise ConnectorError(f"Invalid wallet pair {from_wallet} and {to_wallet}.")
        data = self._binance_api(method, asset=asset.upper(), amount=str(amount))
        return utils.load_transaction_id(data)

    def wallet_borrow(self, schema: str, asset: str, amount: float):
        if schema.lower() == 'margin2':
            method = self._handler.create_margin_loan
        elif schema.lower() == 'futures':
            raise ConnectorError(f"Unavailable method for {schema}.")
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        data = self._binance_api(method, asset=asset.upper(), amount=str(amount))
        return utils.load_transaction_id(data)

    def wallet_repay(self, schema: str, asset: str, amount: float):
        if schema.lower() == 'margin2':
            method = self._handler.repay_margin_loan
        elif schema.lower() == 'futures':
            raise ConnectorError(f"Unavailable method for {schema}.")
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        data = self._binance_api(method, asset=asset.upper(), amount=str(amount))
        return utils.load_transaction_id(data)

    def _binance_api(self, method: callable, **kwargs):
        try:
            resp = method(**kwargs)
        except HTTPError as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.status_code}, {exc.message}")
        except BinanceAPIException as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.code}, {exc.message}")
        except BinanceRequestException as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.message}")

        self.throttle.set(
            key=self._throttle_hash_name,
            **self.__get_limit_header(self.handler.response.headers)
        )

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

    def __get_limit_header(self, headers):
        for h in headers:
            if str(h).startswith('X-MBX-USED-WEIGHT-'):
                rate = h[len('X-MBX-USED-WEIGHT-'):]
                try:
                    return dict(
                        limit=int(headers[h]),
                        reset=self.__parse_reset(rate),
                        scope='rest'
                    )
                except ValueError:
                    pass
            elif str(h).startswith('X-MBX-ORDER-COUNT-'):
                rate = h[len('X-MBX-ORDER-COUNT-'):]
                try:
                    return dict(
                        limit=int(headers[h]),
                        reset=self.__parse_reset(rate),
                        scope='order'
                    )
                except ValueError:
                    pass
        return dict(limit=0, reset=None, scope='rest')

    def __parse_reset(self, rate: str) -> int:
        now = datetime.utcnow()
        if len(rate) < 2:
            return int((now + timedelta(seconds=(60 - now.second))).timestamp())
        try:
            num = int(rate[:-1])
        except ValueError:
            num = 1
        period = rate[len(rate)-1:]
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}.get(period.lower(), 60)
        return int((now + timedelta(seconds=((num * duration) - now.second))).timestamp())

    def __setstate__(self, state):
        self.__dict__ = state
        self.open()

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('_handler', None)
        return state
