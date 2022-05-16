import hashlib
import hmac
import httpx
from typing import Optional, List, Tuple, Union
from mst_gateway.connector.api.stocks.binance import utils
from mst_gateway.exceptions import BinanceAPIException, BinanceRequestException


class BaseBinanceAPIClient:

    API_URL = 'https://api.binance.com/api'
    API_TESTNET_URL = 'https://testnet.binance.vision/api'
    MARGIN_API_URL = 'https://api.binance.com/sapi'
    MARGIN_API_TESTNET_URL = 'https://testnet.binance.vision/api'
    FUTURES_API_URL = 'https://fapi.binance.com/fapi'
    FUTURES_API_TESTNET_URL = 'https://testnet.binancefuture.com/fapi'
    FUTURES_COIN_API_URL = 'https://dapi.binance.com/dapi'
    FUTURES_COIN_API_TESTNET_URL = 'https://testnet.binancefuture.com/dapi'

    V1 = 'v1'
    V2 = 'v2'
    V3 = 'v3'

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        self._api_key = api_key
        self._api_secret = api_secret
        self._testnet = testnet

    def get_method_url(self, method: str) -> Tuple[str, str]:
        api_url = self.API_URL
        margin_api_url = self.MARGIN_API_URL
        futures_api_url = self.FUTURES_API_URL
        futures_coin_api_url = self.FUTURES_COIN_API_URL
        if self._testnet:
            api_url = self.API_TESTNET_URL
            margin_api_url = self.MARGIN_API_TESTNET_URL
            futures_api_url = self.FUTURES_API_TESTNET_URL
            futures_coin_api_url = self.FUTURES_COIN_API_TESTNET_URL
        method_map = {
            'get_server_time': (self.GET, f"{api_url}/{self.V3}/time"),
            'stream_get_listen_key': (self.POST, f"{api_url}/{self.V3}/userDataStream"),
            'margin_stream_get_listen_key': (self.POST, f"{margin_api_url}/{self.V1}/userDataStream"),
            'isolated_margin_stream_get_listen_key': (self.POST, f"{margin_api_url}/{self.V1}/userDataStream/isolated"),
            'futures_stream_get_listen_key': (self.POST, f"{futures_api_url}/{self.V1}/listenKey"),
            'futures_coin_stream_get_listen_key': (self.POST, f"{futures_coin_api_url}/{self.V1}/listenKey"),
            'ping': (self.GET, f"{api_url}/{self.V3}/ping"),
            'margin_ping': (self.GET, f"{api_url}/{self.V3}/ping"),
            'isolated_margin_ping': (self.GET, f"{api_url}/{self.V3}/ping"),
            'futures_ping': (self.GET, f"{futures_api_url}/{self.V1}/ping"),
            'futures_coin_ping': (self.GET, f"{futures_coin_api_url}/{self.V1}/ping"),
            'get_exchange_info': (self.GET, f"{api_url}/{self.V3}/exchangeInfo"),
            'get_futures_exchange_info': (self.GET, f"{futures_api_url}/{self.V1}/exchangeInfo"),
            'get_futures_coin_exchange_info': (self.GET, f"{futures_coin_api_url}/{self.V1}/exchangeInfo"),
            'get_all_margin_symbols': (self.GET, f"{margin_api_url}/{self.V1}/margin/allPairs"),
            'get_all_isolated_margin_symbols': (self.GET, f"{margin_api_url}/{self.V1}/margin/isolated/allPairs"),
            'get_futures_funding_rate': (self.GET, f"{futures_api_url}/{self.V1}/fundingRate"),
            'get_futures_coin_funding_rate': (self.GET, f"{futures_coin_api_url}/{self.V1}/fundingRate"),
            'get_order_book': (self.GET, f"{api_url}/{self.V3}/depth"),
            'get_margin_order_book': (self.GET, f"{api_url}/{self.V3}/depth"),
            'get_isolated_margin_order_book': (self.GET, f"{api_url}/{self.V3}/depth"),
            'get_futures_order_book': (self.GET, f"{futures_api_url}/{self.V1}/depth"),
            'get_futures_coin_order_book': (self.GET, f"{futures_coin_api_url}/{self.V1}/depth"),
            'get_trades': (self.GET, f"{api_url}/{self.V3}/trades"),
            'get_margin_trades': (self.GET, f"{api_url}/{self.V3}/trades"),
            'get_isolated_margin_trades': (self.GET, f"{api_url}/{self.V3}/trades"),
            'get_futures_trades': (self.GET, f"{futures_api_url}/{self.V1}/trades"),
            'get_futures_coin_trades': (self.GET, f"{futures_coin_api_url}/{self.V1}/trades"),
            'get_klines': (self.GET, f"{api_url}/{self.V3}/klines"),
            'get_margin_klines': (self.GET, f"{api_url}/{self.V3}/klines"),
            'get_isolated_margin_klines': (self.GET, f"{api_url}/{self.V3}/klines"),
            'get_futures_klines': (self.GET, f"{futures_api_url}/{self.V1}/klines"),
            'get_futures_coin_klines': (self.GET, f"{futures_coin_api_url}/{self.V1}/klines"),
            'get_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/24hr"),
            'get_margin_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/24hr"),
            'get_isolated_margin_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/24hr"),
            'get_futures_ticker': (self.GET, f"{futures_api_url}/{self.V1}/ticker/24hr"),
            'get_futures_coin_ticker': (self.GET, f"{futures_coin_api_url}/{self.V1}/ticker/24hr"),
            'get_symbol_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/price"),
            'get_margin_symbol_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/price"),
            'get_isolated_margin_symbol_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/price"),
            'get_futures_symbol_ticker': (self.GET, f"{futures_api_url}/{self.V1}/ticker/price"),
            'get_futures_coin_symbol_ticker': (self.GET, f"{futures_coin_api_url}/{self.V1}/ticker/price"),
            'get_order_book_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/bookTicker"),
            'get_margin_order_book_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/bookTicker"),
            'get_isolated_margin_order_book_ticker': (self.GET, f"{api_url}/{self.V3}/ticker/bookTicker"),
            'get_futures_order_book_ticker': (self.GET, f"{futures_api_url}/{self.V1}/ticker/bookTicker"),
            'get_futures_coin_order_book_ticker': (self.GET, f"{futures_coin_api_url}/{self.V1}/ticker/bookTicker"),
            'create_order': (self.POST, f"{api_url}/{self.V3}/order"),
            'create_margin_order': (self.POST, f"{margin_api_url}/{self.V1}/margin/order"),
            'create_isolated_margin_order': (self.POST, f"{margin_api_url}/{self.V1}/margin/order"),
            'create_futures_order': (self.POST, f"{futures_api_url}/{self.V1}/order"),
            'create_futures_coin_order': (self.POST, f"{futures_coin_api_url}/{self.V1}/order"),
            'get_order': (self.GET, f"{api_url}/{self.V3}/order"),
            'get_margin_order': (self.GET, f"{margin_api_url}/{self.V1}/margin/order"),
            'get_isolated_margin_order': (self.GET, f"{margin_api_url}/{self.V1}/margin/order"),
            'get_futures_order': (self.GET, f"{futures_api_url}/{self.V1}/order"),
            'get_futures_coin_order': (self.GET, f"{futures_coin_api_url}/{self.V1}/order"),
            'get_open_orders': (self.GET, f"{api_url}/{self.V3}/openOrders"),
            'get_open_margin_orders': (self.GET, f"{margin_api_url}/{self.V1}/margin/openOrders"),
            'get_open_isolated_margin_orders': (self.GET, f"{margin_api_url}/{self.V1}/margin/openOrders"),
            'get_open_futures_orders': (self.GET, f"{futures_api_url}/{self.V1}/openOrders"),
            'get_open_futures_coin_orders': (self.GET, f"{futures_coin_api_url}/{self.V1}/openOrders"),
            'get_all_orders': (self.GET, f"{api_url}/{self.V3}/allOrders"),
            'get_all_margin_orders': (self.GET, f"{margin_api_url}/{self.V1}/margin/allOrders"),
            'get_all_isolated_margin_orders': (self.GET, f"{margin_api_url}/{self.V1}/margin/allOrders"),
            'get_all_futures_orders': (self.GET, f"{futures_api_url}/{self.V1}/allOrders"),
            'get_all_futures_coin_orders': (self.GET, f"{futures_coin_api_url}/{self.V1}/allOrders"),
            'cancel_order': (self.DELETE, f"{api_url}/{self.V3}/order"),
            'cancel_margin_order': (self.DELETE, f"{margin_api_url}/{self.V1}/margin/order"),
            'cancel_isolated_margin_order': (self.DELETE, f"{margin_api_url}/{self.V1}/margin/order"),
            'cancel_futures_order': (self.DELETE, f"{futures_api_url}/{self.V1}/order"),
            'cancel_futures_coin_order': (self.DELETE, f"{futures_coin_api_url}/{self.V1}/order"),
            'get_futures_position_info': (self.GET, f"{futures_api_url}/{self.V1}/positionRisk"),
            'get_futures_coin_position_info': (self.GET, f"{futures_coin_api_url}/{self.V1}/positionRisk"),
            'change_futures_leverage': (self.POST, f"{futures_api_url}/{self.V1}/leverage"),
            'change_futures_coin_leverage': (self.POST, f"{futures_coin_api_url}/{self.V1}/leverage"),
            'change_futures_margin_type': (self.POST, f"{futures_api_url}/{self.V1}/marginType"),
            'change_futures_coin_margin_type': (self.POST, f"{futures_coin_api_url}/{self.V1}/marginType"),
            'get_futures_leverage_bracket': (self.GET, f"{futures_api_url}/{self.V1}/leverageBracket"),
            'get_futures_coin_leverage_bracket': (self.GET, f"{futures_coin_api_url}/{self.V2}/leverageBracket"),
            'get_futures_mark_price': (self.GET, f"{futures_api_url}/{self.V1}/premiumIndex"),
            'get_futures_coin_mark_price': (self.GET, f"{futures_coin_api_url}/{self.V1}/premiumIndex"),
            'get_public_interest_rate': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/margin/vip/spec/list-all'
            ),
            'get_trade_level': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/account/trade-level/get'
            ),
            'get_margin_trade_level': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/account/trade-level/get'
            ),
            'get_isolated_margin_trade_level': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/account/trade-level/get'
            ),
            'get_futures_trade_level': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/account/futures-trade-level/get'
            ),
            'get_futures_coin_trade_level': (
                self.GET, 'https://www.binance.com/gateway-api/v1/public/delivery/trade-level/get'
            ),
            'get_api_key_permission': (self.GET, f"{margin_api_url}/{self.V1}/account/apiRestrictions"),
            'get_deposit_address': (self.GET, f"{margin_api_url}/{self.V1}/capital/deposit/address"),
            'get_account': (self.GET, f"{api_url}/{self.V3}/account"),
            'get_margin_account': (self.GET, f"{margin_api_url}/{self.V1}/margin/account"),
            'get_isolated_margin_account': (self.GET, f"{margin_api_url}/{self.V1}/margin/isolated/account"),
            'get_futures_account': (self.GET, f"{futures_api_url}/{self.V2}/account"),
            'get_futures_coin_account': (self.GET, f"{futures_coin_api_url}/{self.V1}/account"),
            'get_futures_account_balance': (self.GET, f"{futures_api_url}/{self.V1}/balance"),
            'get_futures_coin_account_balance': (self.GET, f"{futures_coin_api_url}/{self.V1}/balance"),
            'get_assets_balance': (self.GET, f"{api_url}/{self.V3}/account"),
            'get_margin_assets_balance': (self.GET, f"{margin_api_url}/{self.V1}/margin/account"),
            'get_isolated_margin_assets_balance': (self.GET, f"{margin_api_url}/{self.V1}/margin/account"),
            'get_futures_assets_balance': (self.GET, f"{futures_api_url}/{self.V1}/balance"),
            'get_futures_coin_assets_balance': (self.GET, f"{futures_coin_api_url}/{self.V1}/balance"),
            'get_bnb_burn': (self.GET, f"{margin_api_url}/{self.V1}/bnbBurn"),
            'transfer_spot_to_margin': (self.POST, f"{margin_api_url}/{self.V1}/margin/transfer"),
            'transfer_spot_to_isolated_margin': (self.POST, f"{margin_api_url}/{self.V1}/margin/isolated/transfer"),
            'transfer_spot_to_futures': (self.POST, f"{margin_api_url}/{self.V3}/futures/transfer"),
            'transfer_spot_to_futures_coin': (self.POST, f"{margin_api_url}/{self.V1}/futures/transfer"),
            'transfer_margin_to_spot': (self.POST, f"{margin_api_url}/{self.V1}/margin/transfer"),
            'transfer_isolated_margin_to_spot': (self.POST, f"{margin_api_url}/{self.V1}/margin/isolated/transfer"),
            'transfer_futures_to_spot': (self.POST, f"{margin_api_url}/{self.V1}/futures/transfer"),
            'transfer_futures_coin_to_spot': (self.POST, f"{margin_api_url}/{self.V1}/futures/transfer"),
            'get_max_margin_loan': (self.GET, f"{margin_api_url}/{self.V1}/margin/maxBorrowable"),
            'get_futures_loan_configs': (self.GET, f"{margin_api_url}/{self.V2}/futures/loan/configs"),
            'get_futures_loan_wallet': (self.GET, f"{margin_api_url}/{self.V2}/futures/loan/wallet"),
            'create_margin_loan': (self.POST, f"{margin_api_url}/{self.V1}/margin/loan"),
            'create_isolated_margin_loan': (self.POST, f"{margin_api_url}/{self.V1}/margin/loan"),
            'create_futures_loan': (self.POST, f"{margin_api_url}/{self.V1}/futures/loan/borrow"),
            'repay_margin_loan': (self.POST, f"{margin_api_url}/{self.V1}/margin/repay"),
            'repay_isolated_margin_loan': (self.POST, f"{margin_api_url}/{self.V1}/margin/repay"),
            'repay_futures_loan': (self.POST, f"{margin_api_url}/{self.V1}/futures/loan/repay"),
        }
        if method_url := method_map.get(method):
            return method_url
        raise BinanceRequestException('Unknown method')

    def _get_headers(self) -> httpx.Headers:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36'
        }
        if self._api_key:
            headers['X-MBX-APIKEY'] = self._api_key
        return httpx.Headers(headers)

    def _generate_signature(self, data: dict) -> str:
        query_string = '&'.join(f"{k}={v}" for k, v in data.items())
        m = hmac.new(self._api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def _handle_response(self, response: httpx.Response) -> dict:
        if not (200 <= response.status_code < 300):
            raise BinanceAPIException(response, response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException(f"Invalid Response: {response.text}")

    def _isolated_margin_assets_balance(self, data: dict) -> List[dict]:
        assets = {}
        for balance in data.get('assets', []):
            base_asset = balance.get('baseAsset', {})
            quote_asset = balance.get('quoteAsset', {})
            for b in (base_asset, quote_asset):
                asset = b.get('asset')
                if asset in assets:
                    assets[asset].update({
                        'borrowed': float(assets[asset]['borrowed']) + float(b['borrowed']),
                        'free': assets[asset]['free'] + float(b['free']),
                        'interest': float(assets[asset]['interest']) + float(b['interest']),
                        'locked': float(assets[asset]['locked']) + float(b['locked']),
                        'netAsset': assets[asset]['netAsset'] + b['netAsset'],
                    })
                else:
                    assets[asset] = b
        return list(assets.values())


class BinanceAPIClient(BaseBinanceAPIClient):

    def _request_kwargs(self, method, signed: bool = False, force_params: bool = False, **kwargs) -> dict:
        for k, v in dict(kwargs.get('data', {})).items():
            if v is None:
                kwargs['data'].pop(k, None)

        if signed:
            res = self.get_server_time()
            kwargs.setdefault('data', {})['timestamp'] = res['serverTime']
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        if kwargs.get('data'):
            if method.upper() == self.GET.upper() or force_params:
                kwargs['params'] = '&'.join(f"{k}={v}" for k, v in kwargs['data'].items())
                kwargs.pop('data', None)
        else:
            kwargs.pop('data', None)
        return kwargs

    def _request(self, method: str, url: str, signed: bool = False, force_params: bool = False,
                 **params) -> Union[dict, List[dict], List[list]]:
        client = httpx.Client(headers=self._get_headers(),
                              proxies=params.pop('proxies', None),
                              timeout=params.pop('timeout', None))
        kwargs = self._request_kwargs(method, signed, force_params, **params)
        request = client.build_request(method, url, **kwargs)
        self.response = client.send(request)
        client.close()
        return self._handle_response(self.response)

    def get_server_time(self, **params) -> dict:
        method, url = self.get_method_url('get_server_time')
        return self._request(method, url, data=params)

    def stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('stream_get_listen_key')
        res = self._request(method, url, data=params)
        return res['listenKey']

    def margin_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('margin_stream_get_listen_key')
        res = self._request(method, url, data=params)
        return res['listenKey']

    def isolated_margin_stream_get_listen_key(self, symbol: str, **params) -> str:
        method, url = self.get_method_url('isolated_margin_stream_get_listen_key')
        params['symbol'] = symbol
        res = self._request(method, url, data=params)
        return res['listenKey']

    def futures_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('futures_stream_get_listen_key')
        res = self._request(method, url, force_params=True, data=params)
        return res['listenKey']

    def futures_coin_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('futures_coin_stream_get_listen_key')
        res = self._request(method, url, force_params=True, data=params)
        return res['listenKey']

    def ping(self, **params) -> dict:
        method, url = self.get_method_url('ping')
        return self._request(method, url, data=params)

    def margin_ping(self, **params) -> dict:
        method, url = self.get_method_url('margin_ping')
        return self._request(method, url, data=params)

    def isolated_margin_ping(self, **params) -> dict:
        method, url = self.get_method_url('isolated_margin_ping')
        return self._request(method, url, data=params)

    def futures_ping(self, **params) -> dict:
        method, url = self.get_method_url('futures_ping')
        return self._request(method, url, force_params=True, data=params)

    def futures_coin_ping(self, **params) -> dict:
        method, url = self.get_method_url('futures_coin_ping')
        return self._request(method, url, force_params=True, data=params)

    def get_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_exchange_info')
        return self._request(method, url, data=params)

    def get_futures_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_exchange_info')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_exchange_info')
        return self._request(method, url, force_params=True, data=params)

    def get_all_margin_symbols(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_margin_symbols')
        return self._request(method, url, signed=True, data=params)

    def get_all_isolated_margin_symbols(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_isolated_margin_symbols')
        return self._request(method, url, signed=True, data=params)

    def get_futures_funding_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_funding_rate')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_funding_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_funding_rate')
        return self._request(method, url, force_params=True,  data=params)

    def get_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_order_book')
        return self._request(method, url, data=params)

    def get_margin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_order_book')
        return self._request(method, url, data=params)

    def get_isolated_margin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_order_book')
        return self._request(method, url, data=params)

    def get_futures_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_order_book')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_order_book')
        return self._request(method, url, force_params=True, data=params)

    def get_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_trades')
        return self._request(method, url, data=params)

    def get_margin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_trades')
        return self._request(method, url, data=params)

    def get_isolated_margin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_trades')
        return self._request(method, url, data=params)

    def get_futures_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_trades')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_trades')
        return self._request(method, url, force_params=True, data=params)

    def get_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_klines')
        return self._request(method, url, data=params)

    def get_margin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_margin_klines')
        return self._request(method, url, data=params)

    def get_isolated_margin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_isolated_margin_klines')
        return self._request(method, url, data=params)

    def get_futures_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_futures_klines')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_futures_coin_klines')
        return self._request(method, url, force_params=True, data=params)

    def get_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_ticker')
        return self._request(method, url, data=params)

    def get_margin_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_ticker')
        return self._request(method, url, data=params)

    def get_isolated_margin_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_ticker')
        return self._request(method, url, data=params)

    def get_futures_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_ticker')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_ticker')
        return self._request(method, url, force_params=True, data=params)

    def get_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_symbol_ticker')
        return self._request(method, url, data=params)

    def get_margin_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_symbol_ticker')
        return self._request(method, url, data=params)

    def get_isolated_margin_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_symbol_ticker')
        return self._request(method, url, data=params)

    def get_futures_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_symbol_ticker')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_symbol_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_symbol_ticker')
        return self._request(method, url, force_params=True, data=params)

    def get_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_order_book_ticker')
        return self._request(method, url, data=params)

    def get_margin_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_order_book_ticker')
        return self._request(method, url, data=params)

    def get_isolated_margin_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_order_book_ticker')
        return self._request(method, url, data=params)

    def get_futures_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_order_book_ticker')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_order_book_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_order_book_ticker')
        return self._request(method, url, force_params=True,  data=params)

    def create_order(self, **params) -> dict:
        method, url = self.get_method_url('create_order')
        return self._request(method, url, signed=True, data=params)

    def create_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('create_margin_order')
        return self._request(method, url, signed=True, data=params)

    def create_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('create_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def create_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('create_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def create_futures_coin_order(self, **params):
        method, url = self.get_method_url('create_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_order(self, **params) -> dict:
        method, url = self.get_method_url('get_order')
        return self._request(method, url, signed=True, data=params)

    def get_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_order')
        return self._request(method, url, signed=True, data=params)

    def get_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def get_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_open_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_orders')
        return self._request(method, url, signed=True, data=params)

    def get_open_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_margin_orders')
        return self._request(method, url, signed=True, data=params)

    def get_open_isolated_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_isolated_margin_orders')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def get_open_futures_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_futures_orders')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_open_futures_coin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_futures_coin_orders')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_all_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_orders')
        return self._request(method, url, signed=True, data=params)

    def get_all_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_margin_orders')
        return self._request(method, url, signed=True, data=params)

    def get_all_isolated_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_isolated_margin_orders')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def get_all_futures_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_futures_orders')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_all_futures_coin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_futures_coin_orders')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def cancel_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_order')
        return self._request(method, url, signed=True, data=params)

    def cancel_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_margin_order')
        return self._request(method, url, signed=True, data=params)

    def cancel_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def cancel_futures_coin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def cancel_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_position_info(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_position_info')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_position_info(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_position_info')
        res = self._request(method, url, signed=True, force_params=True, data=params)
        if symbol := params.pop('symbol', None):
            params['pair'] = utils.symbol2pair(symbol)
            return [position for position in res if position.get('symbol', '').lower() == symbol.lower()]
        return res

    def change_futures_leverage(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_leverage')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def change_futures_coin_leverage(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_coin_leverage')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def change_futures_margin_type(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_margin_type')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def change_futures_coin_margin_type(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_coin_margin_type')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_leverage_bracket(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_leverage_bracket')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_leverage_bracket(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_leverage_bracket')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_mark_price(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_mark_price')
        return self._request(method, url, force_params=True, data=params)

    def get_futures_coin_mark_price(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_mark_price')
        return self._request(method, url, force_params=True, data=params)

    def get_public_interest_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_public_interest_rate')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_trade_level')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_margin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_trade_level')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_isolated_margin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_trade_level')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_futures_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_trade_level')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_futures_coin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_trade_level')
        res = self._request(method, url, data=params)
        return res.get('data', [])

    def get_api_key_permission(self, **params) -> dict:
        method, url = self.get_method_url('get_api_key_permission')
        return self._request(method, url, signed=True, data=params)

    def get_deposit_address(self, coin: str, network: Optional[str] = None, **params) -> dict:
        method, url = self.get_method_url('get_deposit_address')
        params['coin'] = coin
        if network:
            params['network'] = network
        return self._request(method, url, signed=True, data=params)

    def get_account(self, **params) -> dict:
        method, url = self.get_method_url('get_account')
        return self._request(method, url, signed=True, data=params)

    def get_margin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_account')
        return self._request(method, url, signed=True, data=params)

    def get_isolated_margin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_account')
        return self._request(method, url, signed=True, data=params)

    def get_futures_account(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_account')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_account')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_account_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_account_balance')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_account_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_account_balance')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_assets_balance')
        res = self._request(method, url, signed=True, data=params)
        return res.get('balances', [])

    def get_margin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_assets_balance')
        res = self._request(method, url, signed=True, data=params)
        return res.get('userAssets', [])

    def get_isolated_margin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_assets_balance')
        res = self._request(method, url,  signed=True, data=params)
        return self._isolated_margin_assets_balance(res)

    def get_futures_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_assets_balance')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_futures_coin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_assets_balance')
        return self._request(method, url, signed=True, force_params=True, data=params)

    def get_bnb_burn(self, **params) -> dict:
        method, url = self.get_method_url('get_bnb_burn')
        return self._request(method, url, signed=True, data=params)

    def transfer_spot_to_margin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_margin')
        params['type'] = 1
        return self._request(method, url, signed=True, data=params)

    def transfer_spot_to_isolated_margin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_isolated_margin')
        params['transFrom'] = 'SPOT'
        params['transTo'] = 'ISOLATED_MARGIN'
        return self._request(method, url, signed=True, data=params)

    def transfer_spot_to_futures(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_futures')
        params['type'] = 1
        return self._request(method, url, signed=True, data=params)

    def transfer_spot_to_futures_coin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_futures_coin')
        params['type'] = 3
        return self._request(method, url, signed=True, data=params)

    def transfer_margin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_margin_to_spot')
        params['type'] = 2
        return self._request(method, url, signed=True, data=params)

    def transfer_isolated_margin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_isolated_margin_to_spot')
        params['transFrom'] = 'ISOLATED_MARGIN'
        params['transTo'] = 'SPOT'
        return self._request(method, url, signed=True, data=params)

    def transfer_futures_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_futures_to_spot')
        params['type'] = 2
        return self._request(method, url, signed=True, data=params)

    def transfer_futures_coin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_futures_coin_to_spot')
        params['type'] = 4
        return self._request(method, url, signed=True, data=params)

    def get_max_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('get_max_margin_loan')
        return self._request(method, url, signed=True, data=params)

    def get_futures_loan_configs(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_loan_configs')
        return self._request(method, url, signed=True, data=params)

    def get_futures_loan_wallet(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_loan_wallet')
        return self._request(method, url, signed=True, data=params)

    def create_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('create_margin_loan')
        return self._request(method, url, signed=True, data=params)

    def create_isolated_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('create_isolated_margin_loan')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def create_futures_loan(self, **params) -> dict:
        method, url = self.get_method_url('create_futures_loan')
        return self._request(method, url, signed=True, data=params)

    def repay_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('repay_margin_loan')
        return self._request(method, url, signed=True, data=params)

    def repay_isolated_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('repay_isolated_margin_loan')
        params['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=params)

    def repay_futures_loan(self, **params) -> dict:
        method, url = self.get_method_url('repay_futures_loan')
        return self._request(method, url, signed=True, data=params)


class AsyncBinanceAPIClient(BaseBinanceAPIClient):

    async def _request_kwargs(self, method, signed: bool = False, force_params: bool = False, **kwargs) -> dict:
        for k, v in dict(kwargs.get('data', {})).items():
            if v is None:
                kwargs['data'].pop(k, None)

        if signed:
            res = await self.get_server_time()
            kwargs.setdefault('data', {})['timestamp'] = res['serverTime']
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        if kwargs.get('data'):
            if method.upper() == self.GET.upper() or force_params:
                kwargs['params'] = '&'.join(f"{k}={v}" for k, v in kwargs['data'].items())
                kwargs.pop('data', None)
        else:
            kwargs.pop('data', None)
        return kwargs

    async def _request(self, method: str, url: str, signed: bool = False, force_params: bool = False,
                       **params) -> Union[dict, List[dict], List[list]]:
        client = httpx.AsyncClient(headers=self._get_headers(),
                                   proxies=params.pop('proxies', None),
                                   timeout=params.pop('timeout', None))
        kwargs = await self._request_kwargs(method, signed, force_params, **params)
        request = client.build_request(method, url, **kwargs)
        self.response = await client.send(request)
        await client.aclose()
        return self._handle_response(self.response)

    async def get_server_time(self, **params) -> dict:
        method, url = self.get_method_url('get_server_time')
        return await self._request(method, url, data=params)

    async def stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('stream_get_listen_key')
        res = await self._request(method, url, data=params)
        return res['listenKey']

    async def margin_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('margin_stream_get_listen_key')
        res = await self._request(method, url, data=params)
        return res['listenKey']

    async def isolated_margin_stream_get_listen_key(self, symbol: str, **params) -> str:
        method, url = self.get_method_url('isolated_margin_stream_get_listen_key')
        params['symbol'] = symbol
        res = await self._request(method, url, data=params)
        return res['listenKey']

    async def futures_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('futures_stream_get_listen_key')
        res = await self._request(method, url, force_params=True, data=params)
        return res['listenKey']

    async def futures_coin_stream_get_listen_key(self, **params) -> str:
        method, url = self.get_method_url('futures_coin_stream_get_listen_key')
        res = await self._request(method, url, force_params=True, data=params)
        return res['listenKey']

    async def ping(self, **params) -> dict:
        method, url = self.get_method_url('ping')
        return await self._request(method, url, data=params)

    async def margin_ping(self, **params) -> dict:
        method, url = self.get_method_url('margin_ping')
        return await self._request(method, url, data=params)

    async def isolated_margin_ping(self, **params) -> dict:
        method, url = self.get_method_url('isolated_margin_ping')
        return await self._request(method, url, data=params)

    async def futures_ping(self, **params) -> dict:
        method, url = self.get_method_url('futures_ping')
        return await self._request(method, url, force_params=True, data=params)

    async def futures_coin_ping(self, **params) -> dict:
        method, url = self.get_method_url('futures_coin_ping')
        return await self._request(method, url, force_params=True, data=params)

    async def get_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_exchange_info')
        return await self._request(method, url, data=params)

    async def get_futures_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_exchange_info')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_exchange_info(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_exchange_info')
        return await self._request(method, url, force_params=True, data=params)

    async def get_all_margin_symbols(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_margin_symbols')
        return await self._request(method, url, signed=True, data=params)

    async def get_all_isolated_margin_symbols(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_isolated_margin_symbols')
        return await self._request(method, url, signed=True, data=params)

    async def get_futures_funding_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_funding_rate')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_funding_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_funding_rate')
        return await self._request(method, url, force_params=True, data=params)

    async def get_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_order_book')
        return await self._request(method, url, data=params)

    async def get_margin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_order_book')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_order_book')
        return await self._request(method, url, data=params)

    async def get_futures_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_order_book')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_order_book(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_order_book')
        return await self._request(method, url, force_params=True, data=params)

    async def get_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_trades')
        return await self._request(method, url, data=params)

    async def get_margin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_trades')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_trades')
        return await self._request(method, url, data=params)

    async def get_futures_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_trades')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_trades(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_trades')
        return await self._request(method, url, force_params=True, data=params)

    async def get_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_klines')
        return await self._request(method, url, data=params)

    async def get_margin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_margin_klines')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_isolated_margin_klines')
        return await self._request(method, url, data=params)

    async def get_futures_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_futures_klines')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_klines(self, **params) -> List[list]:
        method, url = self.get_method_url('get_futures_coin_klines')
        return await self._request(method, url, force_params=True, data=params)

    async def get_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_ticker')
        return await self._request(method, url, data=params)

    async def get_margin_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_ticker')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_ticker')
        return await self._request(method, url, data=params)

    async def get_futures_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def get_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_symbol_ticker')
        return await self._request(method, url, data=params)

    async def get_margin_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_symbol_ticker')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_symbol_ticker')
        return await self._request(method, url, data=params)

    async def get_futures_symbol_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_symbol_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_symbol_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_symbol_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def get_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_order_book_ticker')
        return await self._request(method, url, ata=params)

    async def get_margin_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_margin_order_book_ticker')
        return await self._request(method, url, data=params)

    async def get_isolated_margin_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_isolated_margin_order_book_ticker')
        return await self._request(method, url, data=params)

    async def get_futures_order_book_ticker(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_order_book_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_order_book_ticker(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_order_book_ticker')
        return await self._request(method, url, force_params=True, data=params)

    async def create_order(self, **params) -> dict:
        method, url = self.get_method_url('create_order')
        return await self._request(method, url, signed=True, data=params)

    async def create_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('create_margin_order')
        return await self._request(method, url, signed=True, data=params)

    async def create_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('create_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return await self._request(method, url, signed=True, data=params)

    async def create_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('create_futures_order')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def create_futures_coin_order(self, **params):
        method, url = self.get_method_url('create_futures_coin_order')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_order(self, **params) -> dict:
        method, url = self.get_method_url('get_order')
        return await self._request(method, url, signed=True, data=params)

    async def get_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_order')
        return await self._request(method, url, signed=True, data=params)

    async def get_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return await self._request(method, url, signed=True, data=params)

    async def get_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_order')
        return await self._request(method, url, signed=True, force_params=True,  data=params)

    async def get_futures_coin_order(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_order')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_open_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_orders')
        return await self._request(method, url, signed=True, data=params)

    async def get_open_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_margin_orders')
        return await self._request(method, url, signed=True, data=params)

    async def get_open_isolated_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_isolated_margin_orders')
        params['isIsolated'] = 'TRUE'
        return await self._request(method, url, signed=True, data=params)

    async def get_open_futures_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_futures_orders')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_open_futures_coin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_open_futures_coin_orders')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_all_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_orders')
        return await self._request(method, url, signed=True, data=params)

    async def get_all_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_margin_orders')
        return await self._request(method, url, signed=True, data=params)

    async def get_all_isolated_margin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_isolated_margin_orders')
        params['isIsolated'] = 'TRUE'
        return await self._request(method, url, signed=True, data=params)

    async def get_all_futures_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_futures_orders')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_all_futures_coin_orders(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_all_futures_coin_orders')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def cancel_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_order')
        return await self._request(method, url, signed=True, data=params)

    async def cancel_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_margin_order')
        return await self._request(method, url, signed=True, data=params)

    async def cancel_isolated_margin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_isolated_margin_order')
        params['isIsolated'] = 'TRUE'
        return await self._request(method, url, signed=True, data=params)

    async def cancel_futures_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_futures_order')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def cancel_futures_coin_order(self, **params) -> dict:
        method, url = self.get_method_url('cancel_futures_coin_order')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_position_info(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_position_info')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_coin_position_info(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_position_info')
        res = await self._request(method, url, signed=True, force_params=True, data=params)
        if symbol := params.pop('symbol', None):
            params['pair'] = utils.symbol2pair(symbol)
            return [position for position in res if position.get('symbol', '').lower() == symbol.lower()]
        return res

    async def change_futures_leverage(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_leverage')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def change_futures_coin_leverage(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_coin_leverage')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def change_futures_margin_type(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_margin_type')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def change_futures_coin_margin_type(self, **params) -> dict:
        method, url = self.get_method_url('change_futures_coin_margin_type')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_leverage_bracket(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_leverage_bracket')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_coin_leverage_bracket(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_leverage_bracket')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_mark_price(self, **params) -> Union[dict, List[dict]]:
        method, url = self.get_method_url('get_futures_mark_price')
        return await self._request(method, url, force_params=True, data=params)

    async def get_futures_coin_mark_price(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_mark_price')
        return await self._request(method, url, force_params=True, data=params)

    async def get_public_interest_rate(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_public_interest_rate')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_trade_level')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_margin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_trade_level')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_isolated_margin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_trade_level')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_futures_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_trade_level')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_futures_coin_trade_level(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_trade_level')
        res = await self._request(method, url, data=params)
        return res.get('data', [])

    async def get_api_key_permission(self, **params) -> dict:
        method, url = self.get_method_url('get_api_key_permission')
        return await self._request(method, url, signed=True, data=params)

    async def get_deposit_address(self, coin: str, network: Optional[str] = None, **params) -> dict:
        method, url = self.get_method_url('get_deposit_address')
        params['coin'] = coin
        if network:
            params['network'] = network
        return await self._request(method, url, signed=True, data=params)

    async def get_account(self, **params) -> dict:
        method, url = self.get_method_url('get_account')
        return await self._request(method, url, signed=True, data=params)

    async def get_margin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_margin_account')
        return await self._request(method, url, signed=True, data=params)

    async def get_isolated_margin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_isolated_margin_account')
        return await self._request(method, url, signed=True, data=params)

    async def get_futures_account(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_account')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_coin_account(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_coin_account')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_account_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_account_balance')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_coin_account_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_account_balance')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_assets_balance')
        res = await self._request(method, url, signed=True, data=params)
        return res.get('balances', [])

    async def get_margin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_margin_assets_balance')
        res = await self._request(method, url, signed=True, data=params)
        return res.get('userAssets', [])

    async def get_isolated_margin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_isolated_margin_assets_balance')
        res = await self._request(method, url, signed=True, data=params)
        return self._isolated_margin_assets_balance(res)

    async def get_futures_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_assets_balance')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_futures_coin_assets_balance(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_coin_assets_balance')
        return await self._request(method, url, signed=True, force_params=True, data=params)

    async def get_bnb_burn(self, **params) -> dict:
        method, url = self.get_method_url('get_bnb_burn')
        return await self._request(method, url, signed=True, data=params)

    async def transfer_spot_to_margin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_margin')
        params['type'] = 1
        return await self._request(method, url, signed=True, data=params)

    async def transfer_spot_to_isolated_margin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_isolated_margin')
        params['transFrom'] = 'SPOT'
        params['transTo'] = 'ISOLATED_MARGIN'
        return await self._request(method, url, signed=True, data=params)

    async def transfer_spot_to_futures(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_futures')
        params['type'] = 1
        return await self._request(method, url, signed=True, data=params)

    async def transfer_spot_to_futures_coin(self, **params) -> dict:
        method, url = self.get_method_url('transfer_spot_to_futures_coin')
        params['type'] = 3
        return await self._request(method, url, signed=True, data=params)

    async def transfer_margin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_margin_to_spot')
        params['type'] = 2
        return await self._request(method, url, signed=True, data=params)

    async def transfer_isolated_margin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_isolated_margin_to_spot')
        params['transFrom'] = 'ISOLATED_MARGIN'
        params['transTo'] = 'SPOT'
        return await self._request(method, url, signed=True, data=params)

    async def transfer_futures_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_futures_to_spot')
        params['type'] = 2
        return await self._request(method, url, signed=True, data=params)

    async def transfer_futures_coin_to_spot(self, **params) -> dict:
        method, url = self.get_method_url('transfer_futures_coin_to_spot')
        params['type'] = 4
        return await self._request(method, url, signed=True, data=params)

    async def get_max_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('get_max_margin_loan')
        return await self._request(method, url, signed=True, data=params)

    async def get_futures_loan_configs(self, **params) -> List[dict]:
        method, url = self.get_method_url('get_futures_loan_configs')
        return await self._request(method, url, signed=True, data=params)

    async def get_futures_loan_wallet(self, **params) -> dict:
        method, url = self.get_method_url('get_futures_loan_wallet')
        return await self._request(method, url, signed=True, data=params)

    async def create_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('create_margin_loan')
        return await self._request(method, url, signed=True, data=params)

    async def create_isolated_margin_loan(self, **params) -> dict:
        params['isIsolated'] = 'TRUE'
        return await self.create_margin_loan(**params)

    async def create_futures_loan(self, **params) -> dict:
        method, url = self.get_method_url('create_futures_loan')
        return await self._request(method, url, signed=True, data=params)

    async def repay_margin_loan(self, **params) -> dict:
        method, url = self.get_method_url('repay_margin_loan')
        return await self._request(method, url, signed=True, data=params)

    async def repay_isolated_margin_loan(self, **params) -> dict:
        params['isIsolated'] = 'TRUE'
        return await self.repay_margin_loan(**params)

    async def repay_futures_loan(self, **params) -> dict:
        method, url = self.get_method_url('repay_futures_loan')
        return await self._request(method, url, signed=True, data=params)
