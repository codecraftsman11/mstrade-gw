import hashlib
import hmac
import httpx
from typing import List, Optional, Tuple
from .exceptions import BinanceApiException, BinanceRequestException


class BaseBinanceApiClient:

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
        self.response = None

    def get_method_info(self, method_name: str) -> Tuple[str, str]:
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
            'isolated_margin_stream_get_listen_key': (
                self.POST, f"{margin_api_url}/{self.V1}/userDataStream/isolated"
            ),
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
            'get_futures_coin_order_book_ticker': (
                self.GET, f"{futures_coin_api_url}/{self.V1}/ticker/bookTicker"
            ),
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
            'get_futures_account_balance': (self.GET, f"{futures_api_url}/{self.V2}/balance"),
            'get_futures_coin_account_balance': (self.GET, f"{futures_coin_api_url}/{self.V1}/balance"),
            'get_assets_balance': (self.GET, f"{api_url}/{self.V3}/account"),
            'get_margin_assets_balance': (self.GET, f"{margin_api_url}/{self.V1}/margin/account"),
            'get_isolated_margin_assets_balance': (self.GET, f"{margin_api_url}/{self.V1}/margin/account"),
            'get_futures_assets_balance': (self.GET, f"{futures_api_url}/{self.V2}/balance"),
            'get_futures_coin_assets_balance': (self.GET, f"{futures_coin_api_url}/{self.V1}/balance"),
            'get_bnb_burn': (self.GET, f"{margin_api_url}/{self.V1}/bnbBurn"),
            'transfer_spot_to_margin': (self.POST, f"{margin_api_url}/{self.V1}/margin/transfer"),
            'transfer_spot_to_isolated_margin': (
                self.POST, f"{margin_api_url}/{self.V1}/margin/isolated/transfer"
            ),
            'transfer_spot_to_futures': (self.POST, f"{margin_api_url}/{self.V1}/futures/transfer"),
            'transfer_spot_to_futures_coin': (self.POST, f"{margin_api_url}/{self.V1}/futures/transfer"),
            'transfer_margin_to_spot': (self.POST, f"{margin_api_url}/{self.V1}/margin/transfer"),
            'transfer_isolated_margin_to_spot': (
                self.POST, f"{margin_api_url}/{self.V1}/margin/isolated/transfer"
            ),
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
        if info := method_map.get(method_name):
            return info
        raise BinanceRequestException('Unknown method')

    @classmethod
    def get_ratelimit_url(cls, url: str, **kwargs) -> httpx.URL:
        params = '&'.join(f"{k}={v}" for k, v in kwargs.items() if k in (
            'limit',
            'symbol',
            'symbols'
        ))
        return httpx.URL(f"{url}?{params}" if params else url)

    def generate_signature(self, data: dict) -> str:
        query_string = '&'.join(f"{k}={v}" for k, v in data.items())
        m = hmac.new(self._api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def _get_headers(self) -> httpx.Headers:
        headers = {
            'Accept': 'application/json'
        }
        if self._api_key:
            headers['X-MBX-APIKEY'] = self._api_key
        return httpx.Headers(headers)

    def _handle_response(self) -> dict:
        if self.response:
            if not (200 <= self.response.status_code < 300):
                raise BinanceApiException(self.response, self.response.status_code, self.response.text)
            try:
                return self.response.json()
            except ValueError:
                raise BinanceRequestException(f"Invalid Response: {self.response.text}")
        raise BinanceRequestException(f"No response")

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
