import httpx
from copy import deepcopy
from typing import List, Union
from .base import BaseBinanceApiClient


class AsyncBinanceApiClient(BaseBinanceApiClient):

    async def get_request_kwargs(self, method, signed: bool = False, force_params: bool = False, **kwargs) -> dict:
        request_kwargs = deepcopy(kwargs)
        for k, v in dict(request_kwargs.get('data', {})).items():
            if v is None:
                del(request_kwargs['data'][k])

        if signed:
            resp = await self.get_server_time()
            request_kwargs.setdefault('data', {})['timestamp'] = resp['serverTime']
            request_kwargs['data']['signature'] = self.generate_signature(request_kwargs['data'])

        if request_kwargs.get('data'):
            if method.upper() == self.GET.upper() or force_params:
                request_kwargs['params'] = '&'.join(f"{k}={v}" for k, v in request_kwargs['data'].items())
                del(request_kwargs['data'])
        else:
            del(request_kwargs['data'])

        return request_kwargs

    async def _request(self, method: str, url: str, signed: bool = False, force_params: bool = False,
                       **kwargs) -> Union[dict, List[dict], List[list]]:
        client = httpx.AsyncClient(headers=self._get_headers(),
                                   proxies=kwargs['data'].pop('proxies', None),
                                   timeout=kwargs['data'].pop('timeout', None))
        request_kwargs = await self.get_request_kwargs(method, signed, force_params, **kwargs)
        request = client.build_request(method, url, **request_kwargs)
        response = await client.send(request)
        return self._handle_response(response)

    async def get_server_time(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_server_time')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed, force_params = self.get_method_info('stream_get_listen_key')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp['listenKey']

    async def margin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed, force_params = self.get_method_info('margin_stream_get_listen_key')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp['listenKey']

    async def isolated_margin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed, force_params = self.get_method_info('isolated_margin_stream_get_listen_key')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp['listenKey']

    async def futures_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed, force_params = self.get_method_info('futures_stream_get_listen_key')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp['listenKey']

    async def futures_coin_stream_get_listen_key(self, **kwargs) -> str:
        method, url, signed, force_params = self.get_method_info('futures_coin_stream_get_listen_key')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp['listenKey']

    async def ping(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('ping')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def margin_ping(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('margin_ping')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def isolated_margin_ping(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('isolated_margin_ping')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def futures_ping(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('futures_ping')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def futures_coin_ping(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('futures_coin_ping')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_exchange_info(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_exchange_info')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_exchange_info(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_exchange_info')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_exchange_info(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_exchange_info')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_margin_symbols(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_margin_symbols')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_isolated_margin_symbols(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_isolated_margin_symbols')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_funding_rate(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_funding_rate')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_funding_rate(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_funding_rate')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_order_book(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_order_book')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_order_book(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_margin_order_book')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_order_book(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_order_book')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_order_book(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_order_book')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_order_book(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_order_book')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_trades(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_trades')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_trades(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_margin_trades')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_trades(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_trades')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_trades(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_trades')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_trades(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_trades')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_klines(self, **kwargs) -> List[list]:
        method, url, signed, force_params = self.get_method_info('get_klines')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_klines(self, **kwargs) -> List[list]:
        method, url, signed, force_params = self.get_method_info('get_margin_klines')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_klines(self, **kwargs) -> List[list]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_klines')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_klines(self, **kwargs) -> List[list]:
        method, url, signed, force_params = self.get_method_info('get_futures_klines')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_klines(self, **kwargs) -> List[list]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_klines')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_margin_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_futures_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_ticker(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_symbol_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_margin_symbol_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_symbol_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_symbol_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_futures_symbol_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_symbol_ticker(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_symbol_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_order_book_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_margin_order_book_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_order_book_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_order_book_ticker(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_futures_order_book_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_order_book_ticker(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_order_book_ticker')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_isolated_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_futures_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_futures_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_futures_coin_order(self, **kwargs):
        method, url, signed, force_params = self.get_method_info('create_futures_coin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_open_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_open_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_open_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_open_margin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_open_isolated_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_open_isolated_margin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_open_futures_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_open_futures_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_open_futures_coin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_open_futures_coin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_margin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_isolated_margin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_isolated_margin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_futures_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_futures_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_all_futures_coin_orders(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_all_futures_coin_orders')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def cancel_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('cancel_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def cancel_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('cancel_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def cancel_isolated_margin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('cancel_isolated_margin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def cancel_futures_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('cancel_futures_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def cancel_futures_coin_order(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('cancel_futures_coin_order')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_position_info(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_position_info')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_position_info(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_position_info')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def change_futures_leverage(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('change_futures_leverage')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def change_futures_coin_leverage(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('change_futures_coin_leverage')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def change_futures_margin_type(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('change_futures_margin_type')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def change_futures_coin_margin_type(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('change_futures_coin_margin_type')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_leverage_bracket(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_leverage_bracket')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_leverage_bracket(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_leverage_bracket')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_mark_price(self, **kwargs) -> Union[dict, List[dict]]:
        method, url, signed, force_params = self.get_method_info('get_futures_mark_price')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_mark_price(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_mark_price')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_public_interest_rate(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_public_interest_rate')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_trade_level')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_margin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_margin_trade_level')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_isolated_margin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_trade_level')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_futures_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_trade_level')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_futures_coin_trade_level(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_trade_level')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('data', [])

    async def get_api_key_permission(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_api_key_permission')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_deposit_address(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_deposit_address')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_account(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_account')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_margin_account(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_margin_account')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_isolated_margin_account(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_account')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_account(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_account')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_account(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_account')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_account_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_account_balance')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_account_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_account_balance')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_assets_balance')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('balances', [])

    async def get_margin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_margin_assets_balance')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return resp.get('userAssets', [])

    async def get_isolated_margin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_isolated_margin_assets_balance')
        resp = await self._request(method, url, signed, force_params, data=kwargs)
        return self._isolated_margin_assets_balance(resp)

    async def get_futures_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_assets_balance')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_coin_assets_balance(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_coin_assets_balance')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_bnb_burn(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_bnb_burn')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_spot_to_margin(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_spot_to_margin')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_spot_to_isolated_margin(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_spot_to_isolated_margin')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_spot_to_futures(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_spot_to_futures')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_spot_to_futures_coin(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_spot_to_futures_coin')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_margin_to_spot(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_margin_to_spot')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_isolated_margin_to_spot(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_isolated_margin_to_spot')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_futures_to_spot(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_futures_to_spot')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def transfer_futures_coin_to_spot(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('transfer_futures_coin_to_spot')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_max_margin_loan(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_max_margin_loan')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_loan_configs(self, **kwargs) -> List[dict]:
        method, url, signed, force_params = self.get_method_info('get_futures_loan_configs')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def get_futures_loan_wallet(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('get_futures_loan_wallet')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_margin_loan(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_margin_loan')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def create_isolated_margin_loan(self, **kwargs) -> dict:
        return await self.create_margin_loan(**kwargs)

    async def create_futures_loan(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('create_futures_loan')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def repay_margin_loan(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('repay_margin_loan')
        return await self._request(method, url, signed, force_params, data=kwargs)

    async def repay_isolated_margin_loan(self, **kwargs) -> dict:
        return await self.repay_margin_loan(**kwargs)

    async def repay_futures_loan(self, **kwargs) -> dict:
        method, url, signed, force_params = self.get_method_info('repay_futures_loan')
        return await self._request(method, url, signed, force_params, data=kwargs)
