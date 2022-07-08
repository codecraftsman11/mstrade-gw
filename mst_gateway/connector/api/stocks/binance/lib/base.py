import abc
import hashlib
import hmac
import httpx
import time
from abc import abstractmethod
from typing import Optional
from .factory import BinanceMethodFactory
from .exceptions import BinanceAPIException
from ...lib import AbstractApiClient


class BaseBinanceApiClient(AbstractApiClient, abc.ABC):
    method_factory = BinanceMethodFactory()

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        super().__init__(api_key, api_secret, testnet)
        self._timestamp_offset = 0

    @abstractmethod
    def get_client(self, proxies) -> httpx.Client:
        raise NotImplementedError

    def get_method_info(self, method_name: str, **params):
        return self.method_factory.info(method_name, self.testnet, **params)

    def _get_headers(self, optional_headers: Optional[dict]) -> httpx.Headers:
        headers = {
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['X-MBX-APIKEY'] = self.api_key
        if isinstance(optional_headers, dict):
            headers.update(optional_headers)
        return httpx.Headers(headers)

    def generate_signature(self, data: dict) -> str:
        query_string = '&'.join(f"{k}={v}" for k, v in data.items())
        m = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def _prepare_request_params(self, method: str, signed: bool = False, force_params: bool = False, **kwargs) -> dict:
        for k, v in dict(kwargs['data']).items():
            if v is None:
                del(kwargs['data'][k])

        if signed:
            kwargs.setdefault('data', {})['timestamp'] = int(time.time() * 1000 + self._timestamp_offset)
            kwargs['data']['signature'] = self.generate_signature(kwargs['data'])

        if kwargs['data']:
            if method.upper() == self.method_factory.GET.upper() or force_params:
                kwargs['params'] = httpx.QueryParams(**kwargs['data'])
                del(kwargs['data'])
        else:
            del(kwargs['data'])
        return kwargs

    @staticmethod
    def handle_response(response: httpx.Response) -> dict:
        if not (200 <= response.status_code < 300):
            raise BinanceAPIException(response)
        return response.json()
