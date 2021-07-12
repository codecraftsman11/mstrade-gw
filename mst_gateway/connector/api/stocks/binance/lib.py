import time
from binance.client import AsyncClient as BaseAsyncClient, Client as BaseClient
from binance.exceptions import BinanceRequestException


class Client(BaseClient):
    MARGIN_TESTNET_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    MARGIN_API_VERSION2 = 'v2'

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


class AsyncClient(BaseAsyncClient):
    MARGIN_TESTNET_URL = 'https://testnet.binance.vision/sapi'  # margin api does not exist
    MARGIN_API_VERSION2 = 'v2'

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

    async def __aenter__(self):
        res = await self.get_server_time()
        self.timestamp_offset = res['serverTime'] - int(time.time() * 1000)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()
