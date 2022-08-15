import httpx
from .base import BaseBinanceApiClient


class BinanceApiClient(BaseBinanceApiClient):

    def _request(self, method: str, url: httpx.URL, signed: bool = False,
                 force_params: bool = False, **kwargs) -> httpx.Response:
        optional_headers = kwargs['data'].pop('headers', None)
        proxies = kwargs['data'].pop('proxies', None)
        timeout = kwargs['data'].pop('timeout', None)
        headers = self._get_headers(optional_headers)
        request_params = self._prepare_request_params(method, signed, force_params, **kwargs)
        return self.get_client(proxies).request(method, url, headers=headers, timeout=timeout, **request_params)

    def get_client(self, proxies) -> httpx.Client:
        if session := self._session_map.get(proxies):
            return session
        session = httpx.Client(proxies=proxies)
        self._session_map[proxies] = session
        return session

    def get_server_time(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_server_time')
        return self._request(method, url, data=kwargs)

    def stream_get_listen_key(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('stream_get_listen_key')
        return self._request(method, url, data=kwargs)

    def margin_stream_get_listen_key(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('margin_stream_get_listen_key')
        return self._request(method, url, data=kwargs)

    def isolated_margin_stream_get_listen_key(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('isolated_margin_stream_get_listen_key')
        return self._request(method, url, data=kwargs)

    def futures_stream_get_listen_key(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('futures_stream_get_listen_key')
        return  self._request(method, url, force_params=True, data=kwargs)

    def futures_coin_stream_get_listen_key(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('futures_coin_stream_get_listen_key')
        return self._request(method, url, force_params=True, data=kwargs)

    def ping(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('ping')
        return self._request(method, url, data=kwargs)

    def margin_ping(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('margin_ping')
        return self._request(method, url, data=kwargs)

    def isolated_margin_ping(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('isolated_margin_ping')
        return self._request(method, url, data=kwargs)

    def futures_ping(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('futures_ping')
        return self._request(method, url, force_params=True, data=kwargs)

    def futures_coin_ping(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('futures_coin_ping')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_exchange_info(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_exchange_info')
        return self._request(method, url, data=kwargs)

    def get_futures_exchange_info(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_exchange_info')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_exchange_info(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_exchange_info')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_all_margin_symbols(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_margin_symbols')
        return self._request(method, url, signed=True, data=kwargs)

    def get_all_isolated_margin_symbols(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_isolated_margin_symbols')
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_funding_rate(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_funding_rate')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_funding_rate(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_funding_rate')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_order_book(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_margin_order_book(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_order_book(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_futures_order_book(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_order_book(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_trades(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_margin_trades(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_trades(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_futures_trades(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_trades(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_klines(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_margin_klines(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_klines(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, data=kwargs)

    def get_futures_klines(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_klines(self, symbol: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, force_params=True, data=kwargs)

    def get_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_ticker')
        return self._request(method, url, data=kwargs)

    def get_margin_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_ticker')
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_ticker')
        return self._request(method, url, data=kwargs)

    def get_futures_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_symbol_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_symbol_ticker')
        return self._request(method, url, data=kwargs)

    def get_margin_symbol_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_symbol_ticker')
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_symbol_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_symbol_ticker')
        return self._request(method, url, data=kwargs)

    def get_futures_symbol_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_symbol_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_symbol_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_symbol_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_order_book_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_order_book_ticker')
        return self._request(method, url, data=kwargs)

    def get_margin_order_book_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_order_book_ticker')
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_order_book_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_order_book_ticker')
        return self._request(method, url, data=kwargs)

    def get_futures_order_book_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_order_book_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_order_book_ticker(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_order_book_ticker')
        return self._request(method, url, force_params=True, data=kwargs)

    def create_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_order')
        return self._request(method, url, signed=True, data=kwargs)

    def create_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_margin_order')
        return self._request(method, url, signed=True, data=kwargs)

    def create_isolated_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=kwargs)

    def create_futures_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def create_futures_coin_order(self, **kwargs):
        method, url = self.get_method_info('create_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_order')
        return self._request(method, url, signed=True, data=kwargs)

    def get_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_order')
        return self._request(method, url, signed=True, data=kwargs)

    def get_isolated_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_open_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_open_orders')
        return self._request(method, url, signed=True, data=kwargs)

    def get_open_margin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_open_margin_orders')
        return self._request(method, url, signed=True, data=kwargs)

    def get_open_isolated_margin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_open_isolated_margin_orders')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=kwargs)

    def get_open_futures_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_open_futures_orders')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_open_futures_coin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_open_futures_coin_orders')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_all_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_orders')
        return self._request(method, url, signed=True, data=kwargs)

    def get_all_margin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_margin_orders')
        return self._request(method, url, signed=True, data=kwargs)

    def get_all_isolated_margin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_isolated_margin_orders')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, data=kwargs)

    def get_all_futures_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_futures_orders')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_all_futures_coin_orders(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_all_futures_coin_orders')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def cancel_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('cancel_order')
        return self._request(method, url, signed=True, data=kwargs)

    def cancel_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('cancel_margin_order')
        return self._request(method, url, signed=True, data=kwargs)

    def cancel_futures_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('cancel_futures_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def cancel_futures_coin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('cancel_futures_coin_order')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def cancel_isolated_margin_order(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('cancel_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_position_info(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_position_info')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_position_info(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_position_info')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def change_futures_leverage(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('change_futures_leverage')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def change_futures_coin_leverage(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('change_futures_coin_leverage')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def change_futures_margin_type(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('change_futures_margin_type')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def change_futures_coin_margin_type(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('change_futures_coin_margin_type')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_leverage_bracket(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_leverage_bracket')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_leverage_bracket(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_leverage_bracket')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_premium_index(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_premium_index')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_futures_coin_premium_index(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_premium_index')
        return self._request(method, url, force_params=True, data=kwargs)

    def get_public_interest_rate(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_public_interest_rate')
        return self._request(method, url, data=kwargs)

    def get_trade_level(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_trade_level')
        return self._request(method, url, data=kwargs)

    def get_margin_trade_level(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_trade_level')
        return self._request(method, url, data=kwargs)

    def get_isolated_margin_trade_level(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_trade_level')
        return self._request(method, url, data=kwargs)

    def get_futures_trade_level(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_trade_level')
        return self._request(method, url, data=kwargs)

    def get_futures_coin_trade_level(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_trade_level')
        return self._request(method, url, data=kwargs)

    def get_api_key_permission(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_api_key_permission')
        return self._request(method, url, signed=True, data=kwargs)

    def get_deposit_address(self, coin: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_deposit_address')
        kwargs['coin'] = coin
        return self._request(method, url, signed=True, data=kwargs)

    def get_account(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_account')
        return self._request(method, url, signed=True, data=kwargs)

    def get_margin_account(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_account')
        return self._request(method, url, signed=True, data=kwargs)

    def get_isolated_margin_account(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_account')
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_account(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_account')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_account(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_account')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_account_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_account_balance')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_account_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_account_balance')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_assets_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_assets_balance')
        return self._request(method, url, signed=True, data=kwargs)

    def get_margin_assets_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_margin_assets_balance')
        return self._request(method, url, signed=True, data=kwargs)

    def get_isolated_margin_assets_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_isolated_margin_assets_balance')
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_assets_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_assets_balance')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_futures_coin_assets_balance(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_coin_assets_balance')
        return self._request(method, url, signed=True, force_params=True, data=kwargs)

    def get_bnb_burn(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_bnb_burn')
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_spot_to_margin(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_spot_to_margin')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 1
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_spot_to_isolated_margin(self, symbol: str, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_spot_to_isolated_margin')
        kwargs.update({
            'symbol': symbol,
            'asset': asset,
            'amount': amount,
            'transferFrom': 'SPOT',
            'transTo': 'ISOLATED_MARGIN'
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_spot_to_futures(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_spot_to_futures')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 1
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_spot_to_futures_coin(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_spot_to_futures_coin')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 3
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_margin_to_spot(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_margin_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 2
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_isolated_margin_to_spot(self, symbol: str, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_isolated_margin_to_spot')
        kwargs.update({
            'symbol': symbol,
            'asset': asset,
            'amount': amount,
            'transferFrom': 'ISOLATED_MARGIN',
            'transTo': 'SPOT'
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_futures_to_spot(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_futures_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 2
        })
        return self._request(method, url, signed=True, data=kwargs)

    def transfer_futures_coin_to_spot(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('transfer_futures_coin_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 4
        })
        return self._request(method, url, signed=True, data=kwargs)

    def get_max_margin_loan(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_max_margin_loan')
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_loan_configs(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_loan_configs')
        return self._request(method, url, signed=True, data=kwargs)

    def get_futures_loan_wallet(self, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('get_futures_loan_wallet')
        return self._request(method, url, signed=True, data=kwargs)

    def create_margin_loan(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount
        })
        return self._request(method, url, signed=True, data=kwargs)

    def create_isolated_margin_loan(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_isolated_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'isIsolated': 'TRUE'
        })
        return self._request(method, url, signed=True, data=kwargs)

    def create_futures_loan(self, coin: str, collateral_coin: str, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('create_futures_loan')
        kwargs.update({
            'coin': coin,
            'collateralCoin': collateral_coin
        })
        return self._request(method, url, signed=True, data=kwargs)

    def repay_margin_loan(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('repay_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount
        })
        return self._request(method, url, signed=True, data=kwargs)

    def repay_isolated_margin_loan(self, asset: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('repay_isolated_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'isIsolated': 'TRUE'
        })
        return self._request(method, url, signed=True, data=kwargs)

    def repay_futures_loan(self, coin: str, collateral_coin: str, amount: float, **kwargs) -> httpx.Response:
        method, url = self.get_method_info('repay_futures_loan')
        kwargs.update({
            'coin': coin,
            'collateralCoin': collateral_coin,
            'amount': amount
        })
        return self._request(method, url, signed=True, data=kwargs)

    def close(self):
        for session in self._session_map.values():
            session.close()
        self._session_map.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
