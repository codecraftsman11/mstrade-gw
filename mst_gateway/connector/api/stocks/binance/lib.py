import aiohttp
import hmac
import hashlib
import time
from operator import itemgetter
from binance.client import Client as BaseClient
from binance.exceptions import BinanceRequestException


class Client(BaseClient):
    TEST_API_URL = 'https://testnet.binance.vision/api'
    TEST_WITHDRAW_API_URL = 'https://testnet.binance.vision/wapi'
    TEST_MARGIN_API_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    WEBSITE_URL = 'https://www.binance.{}'
    TEST_FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
    FUTURES_API_V2_VERSION = 'v2'
    MARGIN_API_V2_VERSION = 'v2'

    def __init__(self, api_key=None, api_secret=None, requests_params=None, tld='com', test=False):
        super().__init__(api_key=api_key, api_secret=api_secret, requests_params=requests_params, tld=tld)
        self.test = test
        self.API_URL = self._api_url(test, tld)
        self.WITHDRAW_API_URL = self._withdraw_api_url(test, tld)
        self.MARGIN_API_URL = self._margin_api_url(test, tld)
        self.FUTURES_URL = self._futures_api_url(test, tld)

    def _api_url(self, test, tld):
        if test:
            return self.TEST_API_URL
        return self.API_URL.format(tld)

    def _withdraw_api_url(self, test, tld):
        if test:
            return self.TEST_WITHDRAW_API_URL
        return self.WITHDRAW_API_URL.format(tld)

    def _margin_api_url(self, test, tld):
        if test:
            return self.TEST_MARGIN_API_URL
        return self.MARGIN_API_URL.format(tld)

    def _futures_api_url(self, test, tld):
        if test:
            return self.TEST_FUTURES_URL
        return self.FUTURES_URL.format(tld)

    def _create_margin_v2_api_uri(self, path):
        return self.MARGIN_API_URL + '/' + self.MARGIN_API_V2_VERSION + '/' + path

    def _request_margin_v2_api(self, method, path, signed=False, **kwargs):
        uri = self._create_margin_v2_api_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _create_futures_api_v2_uri(self, path):
        return self.FUTURES_URL + '/' + self.FUTURES_API_V2_VERSION + '/' + path

    def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_v2_uri(path)
        return self._request(method, uri, signed, True, **kwargs)

    def _generate_signature(self, data):
        if not (self.API_SECRET and isinstance(self.API_SECRET, str)):
            raise BinanceRequestException('API-key format invalid.')
        return super()._generate_signature(data)

    def futures_transfer_spot_to_futures(self, **params):
        """Execute transfer between spot account and futures account.

        https://binance-docs.github.io/apidocs/futures/en/#new-future-account-transfer

        :param asset: name of the asset
        :type asset: str
        :param amount: amount to transfer
        :type amount: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        .. code:: python

            transfer = client.futures_transfer_spot_to_futures(asset='BTC', amount='1.1')

        :returns: API response

        .. code-block:: python

            {
                "tranId": 100000001
            }

        :raises: BinanceRequestException, BinanceAPIException


        1: transfer from spot main account to future account
        2: transfer from future account to spot main account
        """
        params['type'] = 1
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def futures_transfer_futures_to_spot(self, **params):
        params['type'] = 2
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def get_lending_project_position_list(self, **params):
        """Get Lending Product List

        https://binance-docs.github.io/apidocs/spot/en/#get-customized-fixed-project-position-user_data

        :param asset: required
        :type asset: str
        """
        return self._request_margin_api('get', 'lending/project/position/list', signed=True, data=params)

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

    def futures_account_v2(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#account-information-v2-user_data

        """
        return self._request_futures_api_v2('get', 'account', True, data=params)

    def futures_stream_get_listen_key(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#start-user-data-stream-user_stream

        """
        res = self._request_futures_api('post', 'listenKey', True, data=params)
        return res['listenKey']

    def get_bnb_burn_state(self, **params):
        """Get Lending Product List

        https://binance-docs.github.io/apidocs/spot/en/#toggle-bnb-burn-on-spot-trade-and-margin-interest-user_data

        :returns: API response

        .. code-block:: python
            {
               "spotBNBBurn":true,
               "interestBNBBurn": false
            }
        """
        return self._request_margin_api('get', 'bnbBurn', True, data=params)

    def post_bnb_burn_state(self, **params):
        """Get Lending Product List

        https://binance-docs.github.io/apidocs/spot/en/#toggle-bnb-burn-on-spot-trade-and-margin-interest-user_data

        :param spotBNBBurn: optional
        :type spotBNBBurn: str
        :param interestBNBBurn: optional
        :type interestBNBBurn: str
        """
        return self._request_margin_api('post', 'bnbBurn', True, data=params)

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
        return {}

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


class AsyncClient:
    API_URL = 'https://api.binance.{}/api'
    WITHDRAW_API_URL = 'https://api.binance.{}/wapi'
    MARGIN_API_URL = 'https://api.binance.{}/sapi'
    WEBSITE_URL = 'https://www.binance.{}'
    FUTURES_URL = 'https://fapi.binance.{}/fapi'
    PUBLIC_API_VERSION = 'v1'
    PRIVATE_API_VERSION = 'v3'
    WITHDRAW_API_VERSION = 'v3'
    MARGIN_API_VERSION = 'v1'
    FUTURES_API_VERSION = 'v1'

    TEST_API_URL = 'https://testnet.binance.vision/api'
    TEST_WITHDRAW_API_URL = 'https://testnet.binance.vision/wapi'
    TEST_MARGIN_API_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    TEST_FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
    FUTURES_API_V2_VERSION = 'v2'
    MARGIN_API_V2_VERSION = 'v2'

    def __init__(self, api_key=None, api_secret=None, requests_params=None, tld='com', test=False):
        """Binance API Async Client constructor

        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.
        :param requests_params: optional - Dictionary of requests params to use for all calls
        :type requests_params: dict.

        """
        self.tld = tld
        self.WITHDRAW_API_URL = self.WITHDRAW_API_URL.format(tld)
        self.MARGIN_API_URL = self.MARGIN_API_URL.format(tld)
        self.WEBSITE_URL = self.WEBSITE_URL.format(tld)
        self.FUTURES_URL = self.FUTURES_URL.format(tld)

        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = None
        self._requests_params = requests_params
        self.response = None

        self.test = test

    async def open(self):
        self.session = await self._init_session()
        self.API_URL = await self._api_url(self.test, self.tld)
        self.WITHDRAW_API_URL = await self._withdraw_api_url(self.test, self.tld)
        self.MARGIN_API_URL = await self._margin_api_url(self.test, self.tld)
        self.FUTURES_URL = await self._futures_api_url(self.test, self.tld)

    async def close(self):
        await self.session.close()
        self.session = None
        self.response = None

    async def _init_session(self):
        session = aiohttp.ClientSession()
        session.headers.update({'Accept': 'application/json',
                                'User-Agent': 'binance/python',
                                'X-MBX-APIKEY': self.API_KEY})
        return session

    async def _api_url(self, test, tld):
        if test:
            return self.TEST_API_URL
        return self.API_URL.format(tld)

    async def _withdraw_api_url(self, test, tld):
        if test:
            return self.TEST_WITHDRAW_API_URL
        return self.WITHDRAW_API_URL.format(tld)

    async def _margin_api_url(self, test, tld):
        if test:
            return self.TEST_MARGIN_API_URL
        return self.MARGIN_API_URL.format(tld)

    async def _futures_api_url(self, test, tld):
        if test:
            return self.TEST_FUTURES_URL
        return self.FUTURES_URL.format(tld)

    async def _create_margin_v2_api_uri(self, path):
        return self.MARGIN_API_URL + '/' + self.MARGIN_API_V2_VERSION + '/' + path

    async def _request_margin_v2_api(self, method, path, signed=False, **kwargs):
        uri = await self._create_margin_v2_api_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def _create_futures_api_v2_uri(self, path):
        return self.FUTURES_URL + '/' + self.FUTURES_API_V2_VERSION + '/' + path

    async def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = await self._create_futures_api_v2_uri(path)
        return await self._request(method, uri, signed, True, **kwargs)

    async def _create_api_uri(self, path, signed=True, version=PUBLIC_API_VERSION):
        v = self.PRIVATE_API_VERSION if signed else version
        return self.API_URL + '/' + v + '/' + path

    async def _create_withdraw_api_uri(self, path):
        return self.WITHDRAW_API_URL + '/' + self.WITHDRAW_API_VERSION + '/' + path

    async def _create_margin_api_uri(self, path):
        return self.MARGIN_API_URL + '/' + self.MARGIN_API_VERSION + '/' + path

    async def _create_website_uri(self, path):
        return self.WEBSITE_URL + '/' + path

    async def _create_futures_api_uri(self, path):
        return self.FUTURES_URL + '/' + self.FUTURES_API_VERSION + '/' + path

    async def _generate_signature(self, data):
        if not (self.API_SECRET and isinstance(self.API_SECRET, str)):
            raise BinanceRequestException('API-key format invalid.')
        ordered_data = await self._order_params(data)
        query_string = '&'.join(["{}={}".format(d[0], d[1]) for d in ordered_data])
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    async def _order_params(self, data):
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        # sort parameters by key
        params.sort(key=itemgetter(0))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    async def _request(self, method, uri, signed, force_params=False, **kwargs):

        # set default requests timeout
        kwargs['timeout'] = 10

        # add our global requests params
        if self._requests_params:
            kwargs.update(self._requests_params)

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data

            # find any requests params passed and apply them
            if 'requests_params' in kwargs['data']:
                # merge requests params into kwargs
                kwargs.update(kwargs['data']['requests_params'])
                del(kwargs['data']['requests_params'])

        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = await self._generate_signature(kwargs['data'])

        # sort get and post params to match signature order
        if data:
            # sort post params
            kwargs['data'] = await self._order_params(kwargs['data'])
            # Remove any arguments with values of None.
            null_args = [i for i, (key, value) in enumerate(kwargs['data']) if value is None]
            for i in reversed(null_args):
                del kwargs['data'][i]

        # if get request assign data array to params value for requests lib
        if data and (method == 'get' or force_params):
            kwargs['params'] = '&'.join('%s=%s' % (data[0], data[1]) for data in kwargs['data'])
            del(kwargs['data'])

        self.response = await getattr(self.session, method)(uri, **kwargs)
        return await self._handle_response()

    async def _request_api(self, method, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        uri = await self._create_api_uri(path, signed, version)
        return await self._request(method, uri, signed, **kwargs)

    async def _request_withdraw_api(self, method, path, signed=False, **kwargs):
        uri = await self._create_withdraw_api_uri(path)
        return await self._request(method, uri, signed, True, **kwargs)

    async def _request_margin_api(self, method, path, signed=False, **kwargs):
        uri = await self._create_margin_api_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def _request_website(self, method, path, signed=False, **kwargs):
        uri = await self._create_website_uri(path)
        return await self._request(method, uri, signed, **kwargs)

    async def _request_futures_api(self, method, path, signed=False, **kwargs):
        uri = await self._create_futures_api_uri(path)
        return await self._request(method, uri, signed, True, **kwargs)

    async def _handle_response(self):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not self.response.ok:
            _resp = await self.response.json()
            raise BinanceRequestException(_resp.get('msg'))
        try:
            return await self.response.json()
        except Exception:
            raise BinanceRequestException('APIError: Invalid Response.')

    async def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('get', path, signed, version, **kwargs)

    async def _post(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('post', path, signed, version, **kwargs)

    async def _put(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('put', path, signed, version, **kwargs)

    async def _delete(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return await self._request_api('delete', path, signed, version, **kwargs)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.close()

    async def stream_get_listen_key(self):
        """Start a new user data stream and return the listen key
        If a stream already exists it should return the same key.
        If the stream becomes invalid a new key is returned.

        Can be used to keep the user stream alive.

        https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#start-user-data-stream-user_stream

        :returns: API response

        .. code-block:: python

            {
                "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = await self._post('userDataStream', False, data={}, version=self.PRIVATE_API_VERSION)
        return res['listenKey']

    async def margin_stream_get_listen_key(self):
        """Start a new cross-margin data stream and return the listen key
        If a stream already exists it should return the same key.
        If the stream becomes invalid a new key is returned.

        Can be used to keep the stream alive.

        https://binance-docs.github.io/apidocs/spot/en/#listen-key-margin

        :returns: API response

        .. code-block:: python

            {
                "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
            }

        :raises: BinanceRequestException, BinanceAPIException

        """
        res = await self._request_margin_api('post', 'userDataStream', signed=False, data={})
        return res['listenKey']

    async def futures_stream_get_listen_key(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#start-user-data-stream-user_stream

        """
        res = await self._request_futures_api('post', 'listenKey', True, data=params)
        return res['listenKey']

    async def futures_account_v2(self, **params):
        """Get current account information.

        https://binance-docs.github.io/apidocs/futures/en/#account-information-v2-user_data

        """
        return await self._request_futures_api_v2('get', 'account', True, data=params)

    async def futures_leverage_bracket(self, **params):
        """Notional and Leverage Brackets

        https://binance-docs.github.io/apidocs/futures/en/#notional-and-leverage-brackets-market_data

        """
        return await self._request_futures_api('get', 'leverageBracket', True, data=params)
