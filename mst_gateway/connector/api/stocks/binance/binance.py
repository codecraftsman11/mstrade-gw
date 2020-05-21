from binance.client import Client as BaseClient


class Client(BaseClient):

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
