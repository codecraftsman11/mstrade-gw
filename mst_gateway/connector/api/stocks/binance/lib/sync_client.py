import httpx
from typing import List, Union
from .base import BaseBinanceApiClient


class BinanceApiClient(BaseBinanceApiClient):

    def _get_request_kwargs(self, method: str, signed: bool = False, force_params: bool = False, **kwargs) -> dict:
        for k, v in kwargs['data'].items():
            if v is None:
                del(kwargs['data'][k])

        if signed:
            res = self.get_server_time()
            kwargs.setdefault('data', {})['timestamp'] = res['serverTime']
            kwargs['data']['signature'] = self.generate_signature(kwargs['data'])

        if kwargs['data']:
            if method.upper() == self.GET.upper() or force_params:
                kwargs['params'] = httpx.QueryParams(**kwargs['data'])
                del(kwargs['data'])
        else:
            del(kwargs['data'])

        return kwargs

    def _request(self, method: str, url: str, signed: bool = False, force_params: bool = False,
                 **kwargs) -> Union[dict, List[dict], List[list]]:
        self.response = None
        with httpx.Client(headers=self._get_headers(),
                          proxies=kwargs['data'].pop('proxies', None),
                          timeout=kwargs['data'].pop('timeout', None)) as client:
            kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)
            request = client.build_request(method, url, **kwargs)
            self.response = client.send(request)
        return self._handle_response()

    def get_server_time(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_server_time')
        return self._request(method, url, signed, data=kwargs)

    def stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed = self.get_method_info('stream_get_listen_key')
        resp = self._request(method, url, signed, data=kwargs)
        return resp['listenKey']

    def margin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed = self.get_method_info('margin_stream_get_listen_key')
        resp = self._request(method, url, signed, data=kwargs)
        return resp['listenKey']

    def isolated_margin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed = self.get_method_info('isolated_margin_stream_get_listen_key')
        resp = self._request(method, url, signed, data=kwargs)
        return resp['listenKey']

    def futures_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed = self.get_method_info('futures_stream_get_listen_key')
        resp = self._request(method, url, signed, force_params=True, data=kwargs)
        return resp['listenKey']

    def futures_coin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed = self.get_method_info('futures_coin_stream_get_listen_key')
        resp = self._request(method, url, signed, force_params=True, data=kwargs)
        return resp['listenKey']

    def ping(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('ping')
        return self._request(method, url, signed, data=kwargs)

    def margin_ping(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('margin_ping')
        return self._request(method, url, signed, data=kwargs)

    def isolated_margin_ping(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('isolated_margin_ping')
        return self._request(method, url, signed, data=kwargs)

    def futures_ping(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('futures_ping')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def futures_coin_ping(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('futures_coin_ping')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_exchange_info(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_exchange_info')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_exchange_info(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_exchange_info')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_exchange_info(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_coin_exchange_info')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_all_margin_symbols(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_margin_symbols')
        return self._request(method, url, signed, data=kwargs)

    def get_all_isolated_margin_symbols(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_isolated_margin_symbols')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_funding_rate(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_funding_rate')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_funding_rate(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_funding_rate')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_order_book(self, symbol: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_margin_order_book(self, symbol: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_margin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_order_book(self, symbol: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_isolated_margin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_futures_order_book(self, symbol: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_order_book(self, symbol: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_coin_order_book')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_trades(self, symbol: str, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_margin_trades(self, symbol: str, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_margin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_trades(self, symbol: str, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_isolated_margin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_futures_trades(self, symbol: str, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_trades(self, symbol: str, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_trades')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_klines(self, symbol: str, **kwargs) -> List[list]:
        method, url, signed = self.get_method_info('get_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_margin_klines(self, symbol: str, **kwargs) -> List[list]:
        method, url, signed = self.get_method_info('get_margin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_klines(self, symbol: str, **kwargs) -> List[list]:
        method, url, signed = self.get_method_info('get_isolated_margin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, data=kwargs)

    def get_futures_klines(self, symbol: str, **kwargs) -> List[list]:
        method, url, signed = self.get_method_info('get_futures_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_klines(self, symbol: str, **kwargs) -> List[list]:
        method, url, signed = self.get_method_info('get_futures_coin_klines')
        kwargs['symbol'] = symbol
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_margin_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_margin_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_isolated_margin_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_futures_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_ticker(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_symbol_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_margin_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_margin_symbol_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_isolated_margin_symbol_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_futures_symbol_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_symbol_ticker(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_symbol_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_order_book_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_margin_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_margin_order_book_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_isolated_margin_order_book_ticker')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_futures_order_book_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_order_book_ticker(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_order_book_ticker')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def create_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_order')
        return self._request(method, url, signed, data=kwargs)

    def create_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_margin_order')
        return self._request(method, url, signed, data=kwargs)

    def create_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed, data=kwargs)

    def create_futures_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_futures_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def create_futures_coin_order(self, **kwargs):
        method, url, signed = self.get_method_info('create_futures_coin_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_order')
        return self._request(method, url, signed, data=kwargs)

    def get_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_margin_order')
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed, data=kwargs)

    def get_futures_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_coin_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_open_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_open_orders')
        return self._request(method, url, signed, data=kwargs)

    def get_open_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_open_margin_orders')
        return self._request(method, url, signed, data=kwargs)

    def get_open_isolated_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_open_isolated_margin_orders')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed, data=kwargs)

    def get_open_futures_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_open_futures_orders')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_open_futures_coin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_open_futures_coin_orders')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_all_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_orders')
        return self._request(method, url, signed, data=kwargs)

    def get_all_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_margin_orders')
        return self._request(method, url, signed, data=kwargs)

    def get_all_isolated_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_isolated_margin_orders')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed, data=kwargs)

    def get_all_futures_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_futures_orders')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_all_futures_coin_orders(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_all_futures_coin_orders')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def cancel_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('cancel_order')
        return self._request(method, url, signed, data=kwargs)

    def cancel_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('cancel_margin_order')
        return self._request(method, url, signed, data=kwargs)

    def cancel_futures_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('cancel_futures_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def cancel_futures_coin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('cancel_futures_coin_order')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def cancel_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('cancel_isolated_margin_order')
        kwargs['isIsolated'] = 'TRUE'
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_position_info(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_position_info')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_position_info(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_position_info')
        if symbol := kwargs.pop('symbol', None):
            kwargs['pair'] = symbol.split('_')[0]
            return [position for position in self._request(method, url, signed, force_params=True, data=kwargs)
                    if position.get('symbol', '').lower() == symbol.lower()]
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def change_futures_leverage(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('change_futures_leverage')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def change_futures_coin_leverage(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('change_futures_coin_leverage')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def change_futures_margin_type(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('change_futures_margin_type')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def change_futures_coin_margin_type(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('change_futures_coin_margin_type')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_leverage_bracket(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_leverage_bracket')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_leverage_bracket(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_leverage_bracket')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_mark_price(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed = self.get_method_info('get_futures_mark_price')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_mark_price(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_mark_price')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_public_interest_rate(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_public_interest_rate')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_trade_level')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_margin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_margin_trade_level')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_isolated_margin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_isolated_margin_trade_level')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_futures_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_trade_level')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_futures_coin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_trade_level')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('data', [])

    def get_api_key_permission(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_api_key_permission')
        return self._request(method, url, signed, data=kwargs)

    def get_deposit_address(self, coin: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_deposit_address')
        kwargs['coin'] = coin
        return self._request(method, url, signed, data=kwargs)

    def get_account(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_account')
        return self._request(method, url, signed, data=kwargs)

    def get_margin_account(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_margin_account')
        return self._request(method, url, signed, data=kwargs)

    def get_isolated_margin_account(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_isolated_margin_account')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_account(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_account')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_account(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_coin_account')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_account_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_account_balance')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_account_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_account_balance')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_assets_balance')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('balances', [])

    def get_margin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_margin_assets_balance')
        resp = self._request(method, url, signed, data=kwargs)
        return resp.get('userAssets', [])

    def get_isolated_margin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_isolated_margin_assets_balance')
        resp = self._request(method, url, signed, data=kwargs)
        return self._isolated_margin_assets_balance(resp)

    def get_futures_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_assets_balance')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_futures_coin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_coin_assets_balance')
        return self._request(method, url, signed, force_params=True, data=kwargs)

    def get_bnb_burn(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_bnb_burn')
        return self._request(method, url, signed, data=kwargs)

    def transfer_spot_to_margin(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_spot_to_margin')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 1
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_spot_to_isolated_margin(self, symbol: str, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_spot_to_isolated_margin')
        kwargs.update({
            'symbol': symbol,
            'asset': asset,
            'amount': amount,
            'transferFrom': 'SPOT',
            'transTo': 'ISOLATED_MARGIN'
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_spot_to_futures(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_spot_to_futures')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 1
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_spot_to_futures_coin(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_spot_to_futures_coin')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 3
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_margin_to_spot(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_margin_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 2
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_isolated_margin_to_spot(self, symbol: str, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_isolated_margin_to_spot')
        kwargs.update({
            'symbol': symbol,
            'asset': asset,
            'amount': amount,
            'transferFrom': 'ISOLATED_MARGIN',
            'transTo': 'SPOT'
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_futures_to_spot(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_futures_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 2
        })
        return self._request(method, url, signed, data=kwargs)

    def transfer_futures_coin_to_spot(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('transfer_futures_coin_to_spot')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'type': 4
        })
        return self._request(method, url, signed, data=kwargs)

    def get_max_margin_loan(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_max_margin_loan')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_loan_configs(self, **kwargs) -> List[dict]:
        method, url, signed = self.get_method_info('get_futures_loan_configs')
        return self._request(method, url, signed, data=kwargs)

    def get_futures_loan_wallet(self, **kwargs) -> dict:
        method, url, signed = self.get_method_info('get_futures_loan_wallet')
        return self._request(method, url, signed, data=kwargs)

    def create_margin_loan(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount
        })
        return self._request(method, url, signed, data=kwargs)

    def create_isolated_margin_loan(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_isolated_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'isIsolated': 'TRUE'
        })
        return self._request(method, url, signed, data=kwargs)

    def create_futures_loan(self, coin: str, collateral_coin: str, **kwargs) -> dict:
        method, url, signed = self.get_method_info('create_futures_loan')
        kwargs.update({
            'coin': coin,
            'collateralCoin': collateral_coin
        })
        return self._request(method, url, signed, data=kwargs)

    def repay_margin_loan(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('repay_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount
        })
        return self._request(method, url, signed, data=kwargs)

    def repay_isolated_margin_loan(self, asset: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('repay_isolated_margin_loan')
        kwargs.update({
            'asset': asset,
            'amount': amount,
            'isIsolated': 'TRUE'
        })
        return self._request(method, url, signed, data=kwargs)

    def repay_futures_loan(self, coin: str, collateral_coin: str, amount: float, **kwargs) -> dict:
        method, url, signed = self.get_method_info('repay_futures_loan')
        kwargs.update({
            'coin': coin,
            'collateralCoin': collateral_coin,
            'amount': amount
        })
        return self._request(method, url, signed, data=kwargs)
