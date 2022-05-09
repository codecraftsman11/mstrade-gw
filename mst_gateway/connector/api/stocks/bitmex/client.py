import hashlib
import hmac
import time
from urllib import parse

import requests
from httpx import Client as HttpxClient
from typing import Optional


class BaseClient:
    API_URL = 'https://www.bitmex.com/api'
    API_TESTNET_URL = 'https://testnet.bitmex.com/api'
    API_VERSION = 'v1'

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = True,
                 version: str = 'v1') -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.version = version
        url = self.API_TESTNET_URL if testnet else self.API_URL
        self.base_url = self._generate_base_url(url, version)

    def _generate_base_url(self, url: str, version: str) -> str:
        return f"{url}/{version}"

    def _create_uri(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    def _generate_signature(self, verb: str, path: str, expires: int, data):
        url = f"api/{self.version}/{path}"
        parsed_url = parse.urlparse(url)
        path = parsed_url.path
        r = requests.Request()
        r.prepare()
        if query := parsed_url.query:
            path = f"{path}?{query}"
        message = bytes(verb + path + str(expires) + data, 'utf-8')
        signature = hmac.new(bytes(self.api_secret, 'utf-8'), message, digestmod=hashlib.sha256).hexdigest()
        return signature


class Client(BaseClient):

    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = True,
                 version: str = 'v1') -> None:
        super().__init__(api_key, api_secret, testnet, version)

        # TODO: need to call ping

    def _get_headers(self, uri) -> dict:
        headers = dict()
        if self.api_key and self.api_secret:
            expires = int(round(time.time()) + 5)
            headers['api-expires'] = str(expires)
            headers['api-key'] = self.api_key
            headers['api-signature'] = self._generate_signature(uri)
        return headers

    def _create_request_client(self, uri, proxies: dict = None) -> HttpxClient:
        request = HttpxClient(proxies=proxies)
        headers = self._get_headers(uri)
        request.headers.update(headers)
        return request

    def _request(self, method, uri, proxies: dict = None):
        request = self._create_request_client(uri, proxies)
        kwargs = self._get_request_kwargs()
        response = getattr(request, method)(uri, **kwargs)
        return response

    def _get_request_kwargs(self) -> dict:
        return dict()

    def _handle_response(self) -> dict:
        pass

    # TODO: exchange endpoints abstract methods
