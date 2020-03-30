from bravado.exception import HTTPError
from binance.client import Client
from . import utils
from ...rest import StockRestApi
from .....exceptions import ConnectorError


class BinanceRestApi(StockRestApi):

    def _connect(self, **kwargs):
        return Client(api_key=self._auth['api_key'],
                      api_secret=self._auth['api_secret'])

    def get_user(self) -> dict:
        data = self._binance_api(self._handler.get_account)
        return data

    def get_symbol(self, symbol) -> dict:
        data = self._binance_api(self._handler.get_ticker, symbol=symbol)
        return utils.load_symbol_data(data)

    def list_symbols(self, **kwargs) -> list:
        data = self._binance_api(self._handler.get_ticker)
        return [utils.load_symbol_data(d) for d in data]

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol, limit=1)
        return utils.load_quote_data(data[0], symbol)

    def list_quotes(self, symbol: str, timeframe: str = None, **kwargs) -> list:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol)
        return [utils.load_quote_data(d, symbol) for d in data]

    def list_quote_bins(self, symbol, binsize='1m', count=100, **kwargs):
        data = self._binance_api(
            self._handler.get_klines, symbol=symbol, interval=binsize, limit=count, **self._api_kwargs(kwargs)
        )
        return [utils.load_quote_bin_data(d) for d in data]

    def _binance_api(self, method: callable, **kwargs):
        try:
            resp = method(**kwargs)
            return resp
        except HTTPError as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.status_code}, {exc.message}")

    def _api_kwargs(self, kwargs):
        api_kwargs = dict()
        for _k, _v in kwargs.items():
            if _k == 'date_from':
                api_kwargs['startTime'] = _v
            if _k == 'date_to':
                api_kwargs['endTime'] = _v
        return api_kwargs
