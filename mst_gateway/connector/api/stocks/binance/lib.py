from binance.client import Client as BaseClient
from binance.exceptions import BinanceAPIException
import time


class Client(BaseClient):
    FUTURES_API_V2_VERSION = 'v2'

    def _create_futures_api_v2_uri(self, path):
        return self.FUTURES_URL + '/' + self.FUTURES_API_V2_VERSION + '/' + path

    def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_v2_uri(path)
        return self._request(method, uri, signed, True, **kwargs)

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
