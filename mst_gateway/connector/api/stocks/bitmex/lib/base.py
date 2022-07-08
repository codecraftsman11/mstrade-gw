import abc
import json
import hashlib
import hmac
import time
import httpx
from urllib import parse
from typing import Optional, Union
from .exceptions import BitmexAPIException
from .factory import BitmexMethodFactory
from ...lib import AbstractApiClient


class BaseBitmexApiClient(AbstractApiClient, abc.ABC):
    method_factory = BitmexMethodFactory()

    def get_method_info(self, method_name: str, **params):
        return self.method_factory.info(method_name, self.testnet, **params)

    # Generates an API signature.
    # A signature is HMAC_SHA256(secret, verb + path + nonce + data), hex encoded.
    # Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
    # and the data, if present, must be JSON without whitespace between keys.
    @staticmethod
    def generate_signature(api_secret: str, verb: str, url: str, nonce: Union[str, int], postdict=None):
        """Given an API secret key and data, create a BitMEX-compatible signature."""
        data = ''
        if postdict:
            # separators remove spaces from json
            # BitMEX expects signatures from JSON built without spaces
            data = json.dumps(postdict, separators=(',', ':'))
        parsed_url = parse.urlparse(url)
        path = parsed_url.path
        if query := parsed_url.query:
            path = path + '?' + query
        message = (verb + path + str(nonce) + data).encode('utf-8')
        signature = hmac.new(api_secret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
        return signature

    def _get_headers(self, method: str, url: httpx.URL, optional_headers: Optional[dict],
                     params: Optional[dict]) -> httpx.Headers:
        headers = {
            "Accept": "application/json"
        }
        if self.api_key and self.api_secret:
            expires = str(int(time.time() + 5))
            headers['api-expires'] = expires
            headers['api-key'] = self.api_key
            headers['api-signature'] = self.generate_signature(
                self.api_secret, method, str(httpx.URL(url, params=params)), expires)
        if isinstance(optional_headers, dict):
            headers.update(optional_headers)
        return httpx.Headers(headers)

    def _prepare_request_params(self, **kwargs):
        return {'params': kwargs}

    @staticmethod
    def handle_response(response: httpx.Response) -> dict:
        if not (200 <= response.status_code < 300):
            raise BitmexAPIException(response)
        return response.json()
