from hashlib import sha256
import time
from typing import Dict, Optional
from binance.client import AsyncClient as BaseAsyncClient, Client as BaseClient
from binance.exceptions import BinanceRequestException
from mst_gateway.connector.api.stocks.binance import utils


class Client(BaseClient):
    MARGIN_TESTNET_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    MARGIN_API_VERSION2 = 'v2'

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
        requests_params: Dict[str, str] = None, tld: str = 'com',
        testnet: bool = False, ratelimit_service=None):
        super(Client, self).__init__(api_key, api_secret, requests_params, tld, testnet)
        self.ratelimit = ratelimit_service
        self.key = api_key

    def _generate_hashed_uid(self, key):
        return sha256(key.encode('utf-8')).hexdigest()

    def _get_request_kwargs(self, method, signed: bool, force_params: bool = False, **kwargs) -> Dict:
        # set default requests timeout
        kwargs['timeout'] = 10

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

        # find any requests params passed and apply them
        if data and 'requests_params' in data:
            # merge requests params into kwargs
            kwargs.update(kwargs['data']['requests_params'])
            del (kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000 + self.timestamp_offset)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params and remove any arguments with values of None
            kwargs['data'] = self._order_params(kwargs['data'])

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del(kwargs['data'])

        return kwargs

    def _request(self, method, uri: str, signed: bool, force_params: bool = False, **kwargs) -> Dict:
        hashed_key = self._generate_hashed_uid(self.key)
        result = self.ratelimit.create_reservation(
                                     method=method, url=uri, hashed_uid=hashed_key,
                                 )
        kwargs.setdefault('data', {}).setdefault('requests_params', {})['proxies'] = result
        kwargs = self._get_request_kwargs(method, signed, force_params, **kwargs)
        self.response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(self.response)

    def get_schema_by_method(self, func_name):
        return _method_map(func_name) or f"binance_{int(self.testnet)}"

    def ping(self) -> Dict:
        # disable spot ping for other schemas
        return {}

    def _create_margin_api_uri(self, path: str, version: str = BaseClient.MARGIN_API_VERSION) -> str:
        url = self.MARGIN_API_URL
        if self.testnet:
            url = self.MARGIN_TESTNET_URL
        return url + '/' + version + '/' + path

    def _create_margin_v2_api_uri(self, path):
        return self._create_margin_api_uri(path, self.MARGIN_API_VERSION2)

    def _request_margin_v2_api(self, method, path, signed=False, **kwargs):
        uri = self._create_margin_v2_api_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _create_futures_api_v2_uri(self, path):
        url = self.FUTURES_URL
        if self.testnet:
            url = self.FUTURES_TESTNET_URL
        return url + '/' + self.FUTURES_API_VERSION2 + '/' + path

    def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_v2_uri(path)
        return self._request(method, uri, signed, True, **kwargs)

    def _generate_signature(self, data):
        if not (self.API_SECRET and isinstance(self.API_SECRET, str)):
            raise BinanceRequestException('API-key format invalid.')
        return super()._generate_signature(data)

    def spot_ping(self) -> Dict:
        """Test connectivity to the Rest API.

        https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#test-connectivity

        :returns: Empty array

        .. code-block:: python

            {}

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._get('ping', version=self.PRIVATE_API_VERSION)

    def margin_ping(self) -> Dict:
        return self.spot_ping()

    def isolated_margin_ping(self) -> Dict:
        return self.spot_ping()

    def transfer_spot_to_futures(self, **params):
        """Execute transfer between spot account and futures account.

        https://binance-docs.github.io/apidocs/futures/en/#new-future-account-transfer

        :param asset: name of the asset
        :type asset: str
        :param amount: amount to transfer
        :type amount: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            transfer = client.transfer_spot_to_futures(asset='BTC', amount='1.1')

        :returns: API response

        .. code-block:: python

            {
                "tranId": 100000001
            }

        :raises: BinanceRequestException, BinanceAPIException


        1: transfer from spot main account to futures account
        2: transfer from futures account to spot main account
        3: transfer from spot main account to futures coin account
        4: transfer from futures coin account to spot main account
        """
        params['type'] = 1
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_futures_to_spot(self, **params):
        params['type'] = 2
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_spot_to_futures_coin(self, **params):
        params['type'] = 3
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_futures_coin_to_spot(self, **params):
        params['type'] = 4
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def get_lending_project_position_list(self, **params):
        """Get Lending Product List

        https://binance-docs.github.io/apidocs/spot/en/#get-customized-fixed-project-position-user_data

        :param asset: required
        :type asset: str
        """
        return self._request_margin_api('get', 'lending/project/position/list', signed=True, data=params)

    def get_all_margin_symbols(self, **params):
        """Get All Cross Margin Pairs

            https://binance-docs.github.io/apidocs/spot/en/#get-all-cross-margin-pairs-market_data

        """
        return self._request_margin_api('get', 'margin/allPairs', signed=True, data=params)

    def get_api_key_permission(self, **params):
        """ Get All permissions for api_key

            {
               "ipRestrict": false,
               "createTime": 1623840271000,
               "enableWithdrawals": false,   // This option allows you to withdraw via API. You must apply the
                                             // IP Access Restriction filter in order to enable withdrawals
               "enableInternalTransfer": true,  // This option authorizes this key to transfer funds between
                                                //your master account and your sub account instantly
               "permitsUniversalTransfer": true,  // Authorizes this key to be used for a dedicated universal transfer
                                                  //API to transfer multiple supported currencies. Each business's own
                                                  //transfer API rights are not affected by this authorization
               "enableVanillaOptions": false,  //  Authorizes this key to Vanilla options trading
               "enableReading": true,
               "enableFutures": false,  //  API Key created before your futures account opened does not
                                        //support futures API service
               "enableMargin": false,   //  This option can be adjusted after the Cross Margin account transfer
                                        //is completed
               "enableSpotAndMarginTrading": false, // Spot and margin trading
               "tradingAuthorityExpirationTime": 1628985600000  // Expiration time for spot and margin
                                                                //trading permission
            }

            https://binance-docs.github.io/apidocs/spot/en/#get-api-key-permission-user_data
        """
        return self._request_margin_api('get', 'account/apiRestrictions', signed=True, data=params)

    def get_public_interest_rate(self, **params):
        """
        :returns: API response

        .. code-block:: python
            [
                {
                    "assetName": "MATIC",
                    "specs": [
                        {
                            "vipLevel": "0",
                            "dailyInterestRate": "0.00020000",
                            "borrowLimit": "100000.00000000"
                        }
                    ]
                }
            ]
        """
        uri = 'https://www.binance.com/gateway-api/v1/public/margin/vip/spec/list-all'
        signed = False
        result = self._request('get', uri, signed)
        return result.get('data', [])

    def get_friendly_interest_rate(self, **params):
        """
        :returns: API response

        .. code-block:: python
            [
               {
                  "asset": "ADA",
                  "interestRate": "0.00020000",
                  "effectiveTimestamp": "1584763200000",
                  "duration": "1"
               }
            ]
        """
        uri = 'https://www.binance.com/gateway-api/v1/friendly/margin/interest-rate'
        signed = False
        result = self._request('get', uri, signed, data=params)
        return result.get('data', [])

    def get_trade_level(self, **params):
        """
        :returns: API response

        .. code-block:: python
            [
                {
                    'level': 0,
                    'bnbFloor': 0.0,
                    'bnbCeil': 50.0,
                    'btcFloor': 0.0,
                    'btcCeil': 50.0,
                    'makerCommission': 0.001,
                    'takerCommission': 0.001,
                    'buyerCommission': 0.0,
                    'sellerCommission': 0.0
                }
            ]
        """
        uri = 'https://www.binance.com/gateway-api/v1/public/account/trade-level/get'
        signed = False
        result = self._request('get', uri, signed)
        return result.get('data', [])

    def futures_trade_level(self, **params):
        """
        :returns: API response

        .. code-block:: python
            [
                {
                    'level': 0,
                    'bnbFloor': 0.0,
                    'bnbCeil': 50.0,
                    'btcFloor': 0.0,
                    'btcCeil': 250.0,
                    'makerCommission': 0.0002,
                    'takerCommission': 0.0004,
                    'buyerCommission': 0.0,
                    'sellerCommission': 0.0
                }
            ]
        """
        uri = 'https://www.binance.com/gateway-api/v1/public/account/futures-trade-level/get'
        signed = False
        result = self._request('get', uri, signed)
        return result.get('data', [])

    def futures_coin_trade_level(self, **params):
        """
        :returns: API response

        .. code-block:: python
            [
                {
                    'level': 0,
                    'bnbFloor': 0.0,
                    'bnbCeil': 50.0,
                    'btcFloor': 0.0,
                    'btcCeil': 250.0,
                    'makerCommission': 0.0002,
                    'takerCommission': 0.0004,
                    'buyerCommission': 0.0,
                    'sellerCommission': 0.0
                }
            ]
        """
        uri = 'https://www.binance.com/gateway-api/v1/public/delivery/trade-level/get'
        signed = False
        result = self._request('get', uri, signed)
        return result.get('data', [])

    def futures_account_v2(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#account-information-v2-user_data

        """
        return self._request_futures_api_v2('get', 'account', True, data=params)

    def get_assets_balance(self, **params):
        """Get assets balance.

        https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#account-information-user_data

        :returns: list

        .. code-block:: python

            [
                {
                    "asset": "BTC",
                    "free": "4723846.89208129",
                    "locked": "0.00000000"
                },
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = self.get_account(**params)
        if "balances" in res:
            return res['balances']
        return []

    def get_margin_assets_balance(self, **params):
        """Get assets balance.

        :returns: list

        .. code-block:: python

            [
                {
                    "asset": "BTC",
                    "borrowed": "0.00000000",
                    "free": "0.00499500",
                    "interest": "0.00000000",
                    "locked": "0.00000000",
                    "netAsset": "0.00499500"
                },
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = self.get_margin_account(**params)
        if "userAssets" in res:
            return res['userAssets']
        return []

    def get_isolated_margin_assets_balance(self, **params):
        """Get assets balance.

        :returns: list

        .. code-block:: python

            [
                {
                    "asset": "BTC",
                    "borrowed": "0.00000000",
                    "free": "0.00499500",
                    "interest": "0.00000000",
                    "locked": "0.00000000",
                    "netAsset": "0.00499500"
                },
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = self.get_isolated_margin_account(**params)
        if wallet_data := res.get('assets'):
            assets = {}
            for balance in wallet_data:
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
            return assets.values()
        return []

    def get_futures_assets_balance(self, **params):
        """Get assets balance.

        :returns: list

        .. code-block:: python

            [
                {
                    'accountAlias': 'fWXqfWsRTinY',
                    'asset': 'USDT',
                    'balance': '0.00000000',
                    'withdrawAvailable': '0.00000000',
                    'updateTime': 0
                },
            ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = self.futures_account_balance(**params)
        if res:
            return res
        return []

    def get_futures_coin_assets_balance(self, **params):
        res = self.futures_coin_account_balance(**params)
        if res:
            return res
        return []

    def create_futures_loan(self, **params):
        """Apply for a loan.

        https://binance-docs.github.io/apidocs/spot/en/#borrow-for-cross-collateral-trade

        :param coin: name of the asset
        :type coin: str
        :param amount: amount to transfer(when collateralAmount is empty)
        :type amount: str
        :param collateralCoin: name of the collateral coin
        :type collateralCoin: str
        :param collateralAmount: amount to transfer(when amount is empty)
        :type collateralAmount: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            transaction = client.create_futures_loan(
                                    coin='USDT',
                                    collateralCoin='BUSD',
                                    amount='4.5',
                                    collateralAmount=5.0
                                    )

        :returns: API response

        .. code-block:: python

            {
                "coin": "USDT",
                "amount": "4.50000000",
                "collateralCoin": "BUSD",
                "collateralAmount": "5.00000000",
                "time": 1582540328433,
                "borrowId": "438648398970089472"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._request_margin_api('post', 'futures/loan/borrow', signed=True, data=params)

    def repay_futures_loan(self, **params):
        """Repay loan for futures account.

        https://binance-docs.github.io/apidocs/spot/en/#repay-for-cross-collateral-trade

        :param coin: name of the asset
        :type coin: str
        :param amount: amount to transfer(when collateralAmount is empty)
        :type amount: str
        :param collateralCoin: name of the collateral coin
        :type collateralCoin: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            transaction = client.repay_futures_loan(coin='USDT', collateralCoin='BUSD' amount='1.6')

        :returns: API response

        .. code-block:: python

            {
                "coin": "USDT",
                "amount": "1.68",
                "collateralCoin": "BUSD",
                "repayId": "439659223998894080"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._request_margin_api('post', 'futures/loan/repay', signed=True, data=params)

    def futures_loan_configs(self, **params):
        """Cross-Collateral Information V2

        https://binance-docs.github.io/apidocs/spot/en/#cross-collateral-information-v2-user_data

        :param loanCoin: name of the asset
        :type loanCoin: str
        :param collateralCoin: name of the collateral coin
        :type collateralCoin: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            information = client.futures_loan_configs(loanCoin='USDT', collateralCoin='BUSD')

        :returns: API response

        [
            {
                'collateralCoin': 'BTC',
                'rate': '0.65',
                'marginCallCollateralRate': '0.8',
                'liquidationCollateralRate': '0.9',
                'currentCollateralRate': '0',
                'interestRate': '0.0024',
                'interestGracePeriod': '2',
                'loanCoin': 'USDT'
           },
        ]

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._request_margin_v2_api('get', 'futures/loan/configs', signed=True, data=params)

    def futures_loan_wallet(self, **params):
        """Cross-Collateral Information V2

        https://binance-docs.github.io/apidocs/spot/en/#cross-collateral-wallet-user_data

        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            information = client.futures_loan_configs(**params)

        :returns: API response

        {
            'totalCrossCollateral': '1.69737752',
            'totalBorrowed': '0.99990001', 'asset': 'USD',
            'totalInterest': '0', 'interestFreeLimit': '0',
            'crossCollaterals': [
                {
                    'collateralCoin': 'BTC',
                    'loanCoin': 'BUSD',
                    'locked': '0',
                    'loanAmount': '0',
                    'currentCollateralRate': '0',
                    'principalForInterest': '0',
                    'interest': '0',
                    'interestFreeLimitUsed': '0'
                },
            ]
        }

        :raises: BinanceRequestException, BinanceAPIException

        """
        return self._request_margin_v2_api('get', 'futures/loan/wallet', signed=True, data=params)

    def futures_coin_position_information(self, **params):
        if symbol := params.pop('symbol', None):
            params['pair'] = utils.symbol2pair(symbol)
            return [position for position in super().futures_coin_position_information(**params)
                    if position.get('symbol', '').lower() == symbol.lower()]
        return super().futures_coin_position_information(**params)

    def get_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.get_margin_order(**params)

    def create_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.create_margin_order(**params)

    def cancel_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.cancel_margin_order(**params)

    def get_all_isolated_margin_orders(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.get_all_margin_orders(**params)

    def create_isolated_margin_loan(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.create_margin_loan(**params)

    def repay_isolated_margin_loan(self, **params):
        params['isIsolated'] = 'TRUE'
        return self.repay_margin_loan(**params)


class AsyncClient(BaseAsyncClient):
    MARGIN_TESTNET_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    MARGIN_API_VERSION2 = 'v2'

    def get_schema_by_method(self, func_name):
        return _method_map(func_name) or f"binance_{int(self.testnet)}"

    async def ping(self) -> Dict:
        # disable spot ping for other schemas
        return {}

    def _create_margin_api_uri(self, path: str, version: str = BaseClient.MARGIN_API_VERSION) -> str:
        url = self.MARGIN_API_URL
        if self.testnet:
            url = self.MARGIN_TESTNET_URL
        return url + '/' + version + '/' + path

    def _create_margin_v2_api_uri(self, path):
        return self._create_margin_api_uri(path, self.MARGIN_API_VERSION2)

    async def _request_margin_v2_api(self, method, path, signed=False, **kwargs):
        uri = self._create_margin_v2_api_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    def _create_futures_api_v2_uri(self, path):
        url = self.FUTURES_URL
        if self.testnet:
            url = self.FUTURES_TESTNET_URL
        return url + '/' + self.FUTURES_API_VERSION2 + '/' + path

    async def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_v2_uri(path)
        return await self._request(method, uri, signed, True, **kwargs)

    def _generate_signature(self, data):
        if not (self.API_SECRET and isinstance(self.API_SECRET, str)):
            raise BinanceRequestException('API-key format invalid.')
        return super()._generate_signature(data)

    async def futures_account_v2(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#account-information-v2-user_data

        """
        return await self._request_futures_api_v2('get', 'account', True, data=params)

    async def spot_ping(self) -> Dict:
        return await self._get('ping', version=self.PRIVATE_API_VERSION)

    async def margin_ping(self) -> Dict:
        return await self.spot_ping()

    async def __aenter__(self):
        res = await self.get_server_time()
        self.timestamp_offset = res['serverTime'] - int(time.time() * 1000)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def get_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.get_margin_order(**params)

    async def create_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.create_margin_order(**params)

    async def cancel_isolated_margin_order(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.cancel_margin_order(**params)

    async def get_all_isolated_margin_orders(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.get_all_margin_orders(**params)

    async def create_isolated_margin_loan(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.create_margin_loan(**params)

    async def repay_isolated_margin_loan(self, **params):
        params['isIsolated'] = 'TRUE'
        return await self.repay_margin_loan(**params)

    async def futures_loan_wallet(self, **params):
        return await self._request_margin_v2_api('get', 'futures/loan/wallet', signed=True, data=params)


def _method_map(func_name: str):
    hash_map = {
        # exchange
        'spot_ping': 'exchange',
        'margin_ping': 'exchange',
        'isolated_margin_ping': 'exchange',
        'get_deposit_address': 'exchange',
        'get_ticker': 'exchange',
        'get_products': 'exchange',
        'get_exchange_info': 'exchange',
        'get_symbol_info': 'exchange',
        'get_all_tickers': 'exchange',
        'get_klines': 'exchange',
        'create_order': 'exchange',
        'cancel_order': 'exchange',
        'get_order': 'exchange',
        'get_open_orders': 'exchange',
        'get_all_orders': 'exchange',
        'get_recent_trades': 'exchange',
        'get_order_book': 'exchange',
        'get_account': 'exchange',
        'get_public_interest_rate': 'exchange',
        'get_assets_balance': 'exchange',
        'get_symbol_ticker': 'exchange',
        'get_trade_level': 'exchange',

        # margin2
        'get_all_margin_symbols': 'margin2',
        'create_margin_order': 'margin2',
        'cancel_margin_order': 'margin2',
        'get_margin_order': 'margin2',
        'get_open_margin_orders': 'margin2',
        'get_all_margin_orders': 'margin2',
        'get_margin_account': 'margin2',
        'get_max_margin_loan': 'margin2',
        'get_margin_assets_balance': 'margin2',
        'transfer_spot_to_margin': 'margin2',
        'transfer_spot_to_futures': 'margin2',
        'transfer_spot_to_futures_coin': 'margin2',
        'transfer_margin_to_spot': 'margin2',
        'transfer_futures_to_spot': 'margin2',
        'transfer_futures_coin_to_spot': 'margin2',
        'create_margin_loan': 'margin2',
        'create_futures_loan': 'margin2',
        'repay_margin_loan': 'margin2',
        'repay_futures_loan': 'margin2',
        'get_bnb_burn_spot_margin': 'margin2',

        'get_isolated_margin_order': 'margin2',
        'create_isolated_margin_order': 'margin2',
        'cancel_isolated_margin_order': 'margin2',
        'get_all_isolated_margin_orders': 'margin2',
        'get_isolated_margin_assets_balance': 'margin2',
        'create_isolated_margin_loan': 'margin2',
        'repay_isolated_margin_loan': 'margin2',
        'transfer_spot_to_isolated_margin': 'margin2',
        'transfer_isolated_margin_to_spot': 'margin2',

        # margin3
        'get_all_isolated_margin_symbols': 'margin3',


        # futures
        'futures_ping': 'futures',
        'futures_ticker': 'futures',
        'futures_orderbook_ticker': 'futures',
        'futures_mark_price': 'futures',
        'futures_exchange_info': 'futures',
        'futures_leverage_bracket': 'futures',
        'futures_klines': 'futures',
        'futures_create_order': 'futures',
        'futures_cancel_order': 'futures',
        'futures_get_order': 'futures',
        'futures_get_open_orders': 'futures',
        'futures_get_all_orders': 'futures',
        'futures_recent_trades': 'futures',
        'futures_order_book': 'futures',
        'futures_account_v2': 'futures',
        'futures_loan_wallet': 'futures',
        'futures_loan_configs': 'futures',
        'get_futures_assets_balance': 'futures',
        'futures_symbol_ticker': 'futures',
        'futures_trade_level': 'futures',
        'futures_funding_rate': 'futures',
        'futures_position_information': 'futures',
        'futures_change_margin_type': 'futures',
        'futures_change_leverage': 'futures',


        # futures_coin
        'futures_coin_ping': 'futures_coin',
        'futures_coin_ticker': 'futures_coin',
        'futures_coin_orderbook_ticker': 'futures_coin',
        'futures_coin_mark_price': 'futures_coin',
        'futures_coin_exchange_info': 'futures_coin',
        'futures_coin_leverage_bracket': 'futures_coin',
        'futures_coin_klines': 'futures_coin',
        'futures_coin_create_order': 'futures_coin',
        'futures_coin_cancel_order': 'futures_coin',
        'futures_coin_get_order': 'futures_coin',
        'futures_coin_get_open_orders': 'futures_coin',
        'futures_coin_get_all_orders': 'futures_coin',
        'futures_coin_recent_trades': 'futures_coin',
        'futures_coin_order_book': 'futures_coin',
        'futures_coin_account': 'futures_coin',
        'get_futures_coin_assets_balance': 'futures_coin',
        'futures_coin_symbol_ticker': 'futures_coin',
        'futures_coin_trade_level': 'futures_coin',
        'futures_coin_funding_rate': 'futures_coin',
        'futures_coin_position_information': 'futures_coin',
        'futures_coin_change_margin_type': 'futures_coin',
        'futures_coin_change_leverage': 'futures_coin',
    }
    return hash_map.get(func_name)
