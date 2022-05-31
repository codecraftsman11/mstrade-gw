import httpx
from typing import List, Optional, Union
from .base import BaseBinanceApiClient


class AsyncBinanceApiClient(BaseBinanceApiClient):

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
        if symbol := params.pop('symbol', None):
            params['pair'] = symbol.split('_')[0]
            res = await self._request(method, url, signed=True, force_params=True, data=params)
            return [position for position in res if position.get('symbol', '').lower() == symbol.lower()]
        return await self._request(method, url, signed=True, force_params=True, data=params)

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
