import httpx
from typing import Tuple


class BinanceMethodFactory:

    API_URL = 'https://api.binance.com/api'
    API_TESTNET_URL = 'https://testnet.binance.vision/api'
    MARGIN_API_URL = 'https://api.binance.com/sapi'
    MARGIN_API_TESTNET_URL = ''  # NotImplemented
    FUTURES_API_URL = 'https://fapi.binance.com/fapi'
    FUTURES_API_TESTNET_URL = 'https://testnet.binancefuture.com/fapi'
    FUTURES_COIN_API_URL = 'https://dapi.binance.com/dapi'
    FUTURES_COIN_API_TESTNET_URL = 'https://testnet.binancefuture.com/dapi'

    PUBLIC_API_URL = 'https://www.binance.com/gateway-api'
    PUBLIC_API_TESTNET_URL = 'https://www.binance.com/gateway-api'  # use same on testnet

    V1 = 'v1'
    V2 = 'v2'
    V3 = 'v3'

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    @classmethod
    def info(cls, method_name, testnet=False, **params) -> Tuple[str, httpx.URL]:
        return getattr(cls, method_name)(testnet, **params)

    @classmethod
    def _api_url(cls, testnet=False):
        return cls.API_TESTNET_URL if testnet else cls.API_URL

    @classmethod
    def _margin_api_url(cls, testnet=False):
        return cls.MARGIN_API_TESTNET_URL if testnet else cls.MARGIN_API_URL

    @classmethod
    def _futures_api_url(cls, testnet=False):
        return cls.FUTURES_API_TESTNET_URL if testnet else cls.FUTURES_API_URL

    @classmethod
    def _futures_coin_api_url(cls, testnet=False):
        return cls.FUTURES_COIN_API_TESTNET_URL if testnet else cls.FUTURES_COIN_API_URL

    @classmethod
    def _public_api_url(cls, testnet=False):
        return cls.PUBLIC_API_TESTNET_URL if testnet else cls.PUBLIC_API_URL

    @classmethod
    def get_server_time(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/time", params=params)

    @classmethod
    def stream_get_listen_key(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/userDataStream", params=params)

    @classmethod
    def margin_stream_get_listen_key(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/userDataStream", params=params)

    @classmethod
    def isolated_margin_stream_get_listen_key(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/userDataStream/isolated", params=params)

    @classmethod
    def futures_stream_get_listen_key(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/listenKey", params=params)

    @classmethod
    def futures_coin_stream_get_listen_key(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/listenKey", params=params)

    @classmethod
    def ping(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/ping", params=params)

    @classmethod
    def margin_ping(cls, testnet=False, **params):
        return cls.ping(testnet, **params)

    @classmethod
    def isolated_margin_ping(cls, testnet=False, **params):
        return cls.ping(testnet, **params)

    @classmethod
    def futures_ping(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/ping", params=params)

    @classmethod
    def futures_coin_ping(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/ping", params=params)

    @classmethod
    def get_exchange_info(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/exchangeInfo", params=params)

    @classmethod
    def get_futures_exchange_info(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/exchangeInfo", params=params)

    @classmethod
    def get_futures_coin_exchange_info(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/exchangeInfo", params=params)

    @classmethod
    def get_all_margin_symbols(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/allPairs", params=params)

    @classmethod
    def get_all_isolated_margin_symbols(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/isolated/allPairs", params=params)

    @classmethod
    def get_futures_funding_rate(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/fundingRate", params=params)

    @classmethod
    def get_futures_coin_funding_rate(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/fundingRate", params=params)

    @classmethod
    def get_order_book(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/depth", params=params)

    @classmethod
    def get_margin_order_book(cls, testnet=False, **params):
        return cls.get_order_book(testnet, **params)

    @classmethod
    def get_isolated_margin_order_book(cls, testnet=False, **params):
        return cls.get_order_book(testnet, **params)

    @classmethod
    def get_futures_order_book(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/depth", params=params)

    @classmethod
    def get_futures_coin_order_book(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/depth", params=params)

    @classmethod
    def get_trades(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/trades", params=params)

    @classmethod
    def get_margin_trades(cls, testnet=False, **params):
        return cls.get_trades(testnet, **params)

    @classmethod
    def get_isolated_margin_trades(cls, testnet=False, **params):
        return cls.get_trades(testnet, **params)

    @classmethod
    def get_futures_trades(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/trades", params=params)

    @classmethod
    def get_futures_coin_trades(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/trades", params=params)

    @classmethod
    def get_klines(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/klines", params=params)

    @classmethod
    def get_margin_klines(cls, testnet=False, **params):
        return cls.get_klines(testnet, **params)

    @classmethod
    def get_isolated_margin_klines(cls, testnet=False, **params):
        return cls.get_klines(testnet, **params)

    @classmethod
    def get_futures_klines(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/klines", params=params)

    @classmethod
    def get_futures_coin_klines(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/klines", params=params)

    @classmethod
    def get_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/ticker/24hr", params=params)

    @classmethod
    def get_margin_ticker(cls, testnet=False, **params):
        return cls.get_ticker(testnet, **params)

    @classmethod
    def get_isolated_margin_ticker(cls, testnet=False, **params):
        return cls.get_ticker(testnet, **params)

    @classmethod
    def get_futures_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/ticker/24hr", params=params)

    @classmethod
    def get_futures_coin_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/ticker/24hr", params=params)

    @classmethod
    def get_symbol_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/ticker/price", params=params)

    @classmethod
    def get_margin_symbol_ticker(cls, testnet=False, **params):
        return cls.get_symbol_ticker(testnet, **params)

    @classmethod
    def get_isolated_margin_symbol_ticker(cls, testnet=False, **params):
        return cls.get_symbol_ticker(testnet, **params)

    @classmethod
    def get_futures_symbol_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/ticker/price", params=params)

    @classmethod
    def get_futures_coin_symbol_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/ticker/price", params=params)

    @classmethod
    def get_order_book_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/ticker/bookTicker", params=params)

    @classmethod
    def get_margin_order_book_ticker(cls, testnet=False, **params):
        return cls.get_order_book_ticker(testnet, **params)

    @classmethod
    def get_isolated_margin_order_book_ticker(cls, testnet=False, **params):
        return cls.get_order_book_ticker(testnet, **params)

    @classmethod
    def get_futures_order_book_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/ticker/bookTicker", params=params)

    @classmethod
    def get_futures_coin_order_book_ticker(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/ticker/bookTicker", params=params)

    @classmethod
    def create_order(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/order", params=params)

    @classmethod
    def create_margin_order(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/order", params=params)

    @classmethod
    def create_isolated_margin_order(cls, testnet=False, **params):
        return cls.create_margin_order(testnet, **params)

    @classmethod
    def create_futures_order(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def create_futures_coin_order(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def get_order(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/order", params=params)

    @classmethod
    def get_margin_order(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/order", params=params)

    @classmethod
    def get_isolated_margin_order(cls, testnet=False, **params):
        return cls.get_margin_order(testnet, **params)

    @classmethod
    def get_futures_order(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def get_futures_coin_order(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def get_open_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/openOrders", params=params)

    @classmethod
    def get_open_margin_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/openOrders", params=params)

    @classmethod
    def get_open_isolated_margin_orders(cls, testnet=False, **params):
        return cls.get_open_margin_orders(testnet, **params)

    @classmethod
    def get_open_futures_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/openOrders", params=params)

    @classmethod
    def get_open_futures_coin_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/openOrders", params=params)

    @classmethod
    def get_all_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/allOrders", params=params)

    @classmethod
    def get_all_margin_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/allOrders", params=params)

    @classmethod
    def get_all_isolated_margin_orders(cls, testnet=False, **params):
        return cls.get_all_margin_orders(testnet, **params)

    @classmethod
    def get_all_futures_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/allOrders", params=params)

    @classmethod
    def get_all_futures_coin_orders(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/allOrders", params=params)

    @classmethod
    def cancel_order(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/order", params=params)

    @classmethod
    def cancel_margin_order(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/order", params=params)

    @classmethod
    def cancel_isolated_margin_order(cls, testnet=False, **params):
        return cls.cancel_margin_order(testnet, **params)

    @classmethod
    def cancel_futures_order(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def cancel_futures_coin_order(cls, testnet=False, **params):
        return cls.DELETE, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/order", params=params)

    @classmethod
    def get_futures_position_info(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/positionRisk", params=params)

    @classmethod
    def get_futures_coin_position_info(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/positionRisk", params=params)

    @classmethod
    def change_futures_leverage(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/leverage", params=params)

    @classmethod
    def change_futures_coin_leverage(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/leverage", params=params)

    @classmethod
    def change_futures_margin_type(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/marginType", params=params)

    @classmethod
    def change_futures_coin_margin_type(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/marginType", params=params)

    @classmethod
    def get_futures_leverage_bracket(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/leverageBracket", params=params)

    @classmethod
    def get_futures_coin_leverage_bracket(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V2}/leverageBracket", params=params)

    @classmethod
    def get_futures_mark_price(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V1}/premiumIndex", params=params)

    @classmethod
    def get_futures_coin_mark_price(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/premiumIndex", params=params)

    @classmethod
    def get_public_interest_rate(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._public_api_url(testnet)}/{cls.V1}/public/margin/vip/spec/list-all",
                                  params=params)

    @classmethod
    def get_trade_level(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._public_api_url(testnet)}/{cls.V1}/public/account/trade-level/get",
                                  params=params)

    @classmethod
    def get_margin_trade_level(cls, testnet=False, **params):
        return cls.get_trade_level(testnet, **params)

    @classmethod
    def get_isolated_margin_trade_level(cls, testnet=False, **params):
        return cls.get_trade_level(testnet, **params)

    @classmethod
    def get_futures_trade_level(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._public_api_url(testnet)}/{cls.V1}/public/account/futures-trade-level/get",
                                  params=params)

    @classmethod
    def get_futures_coin_trade_level(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._public_api_url(testnet)}/{cls.V1}/public/delivery/trade-level/get",
                                  params=params)

    @classmethod
    def get_api_key_permission(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/account/apiRestrictions", params=params)

    @classmethod
    def get_deposit_address(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/capital/deposit/address", params=params)

    @classmethod
    def get_account(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/account", params=params)

    @classmethod
    def get_margin_account(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/account", params=params)

    @classmethod
    def get_isolated_margin_account(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/isolated/account", params=params)

    @classmethod
    def get_futures_account(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V2}/account", params=params)

    @classmethod
    def get_futures_coin_account(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/account", params=params)

    @classmethod
    def get_futures_account_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V2}/balance", params=params)

    @classmethod
    def get_futures_coin_account_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/balance", params=params)

    @classmethod
    def get_assets_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._api_url(testnet)}/{cls.V3}/account", params=params)

    @classmethod
    def get_margin_assets_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/account", params=params)

    @classmethod
    def get_isolated_margin_assets_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/account", params=params)

    @classmethod
    def get_futures_assets_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_api_url(testnet)}/{cls.V2}/balance", params=params)

    @classmethod
    def get_futures_coin_assets_balance(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._futures_coin_api_url(testnet)}/{cls.V1}/balance", params=params)

    @classmethod
    def get_bnb_burn(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/bnbBurn", params=params)

    @classmethod
    def transfer_spot_to_margin(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/transfer", params=params)

    @classmethod
    def transfer_spot_to_isolated_margin(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/isolated/transfer", params=params)

    @classmethod
    def transfer_spot_to_futures(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/transfer", params=params)

    @classmethod
    def transfer_spot_to_futures_coin(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/transfer", params=params)

    @classmethod
    def transfer_margin_to_spot(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/transfer", params=params)

    @classmethod
    def transfer_isolated_margin_to_spot(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/isolated/transfer", params=params)

    @classmethod
    def transfer_futures_to_spot(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/transfer", params=params)

    @classmethod
    def transfer_futures_coin_to_spot(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/transfer", params=params)

    @classmethod
    def get_max_margin_loan(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/maxBorrowable", params=params)

    @classmethod
    def get_futures_loan_configs(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V2}/futures/loan/configs", params=params)

    @classmethod
    def get_futures_loan_wallet(cls, testnet=False, **params):
        return cls.GET, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V2}/futures/loan/wallet", params=params)

    @classmethod
    def create_margin_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/loan", params=params)

    @classmethod
    def create_isolated_margin_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/loan", params=params)

    @classmethod
    def create_futures_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/loan/borrow", params=params)

    @classmethod
    def repay_margin_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/repay", params=params)

    @classmethod
    def repay_isolated_margin_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/margin/repay", params=params)

    @classmethod
    def repay_futures_loan(cls, testnet=False, **params):
        return cls.POST, httpx.URL(f"{cls._margin_api_url(testnet)}/{cls.V1}/futures/loan/repay", params=params)
