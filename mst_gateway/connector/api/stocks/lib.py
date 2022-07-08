import abc
import httpx
from abc import abstractmethod
from typing import Optional


class AbstractApiClient(abc.ABC):
    method_factory = None   # method factory class

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self._session_map = {}

    @abstractmethod
    def get_client(self, proxies) -> httpx.Client:
        raise NotImplementedError

    @abstractmethod
    def get_method_info(self, method_name: str, **params):
        raise NotImplementedError
