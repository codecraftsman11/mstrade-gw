from __future__ import annotations
from typing import (
    Optional,
    TYPE_CHECKING,
    Tuple
)
from abc import (
    ABCMeta,
    abstractmethod
)

if TYPE_CHECKING:
    from . import StockWssApi


class Serializer:
    __metaclass__ = ABCMeta
    subscription = "base"

    def __init__(self, wss_api: StockWssApi):
        self._wss_api = wss_api
        self._state = None

    def prefetch(self, message: dict) -> None:
        pass

    @abstractmethod
    async def _get_data(self, message: any) -> Tuple[str, list]:
        raise NotImplementedError

    def _get_state(self, symbol: str = None) -> Optional[list]:
        if self._state is None:
            return None
        if symbol is None:
            return [self._state[k] for k in self._state]
        if symbol.lower() in self._state:
            return [self._state[symbol.lower()]]
        return None

    def _update_state(self, symbol: str, data: any):
        if self._state is None:
            self._state = dict()
        self._state[symbol.lower()] = data

    async def data(self, message) -> Optional[dict]:
        (action, data) = await self._get_data(message)
        if not data:
            return None
        return {
            'acc': self._wss_api.account_name,
            'tb': self.subscription,
            'sch': self._wss_api.schema,
            'act': action,
            'd': data
        }

    def state(self, symbol: str = None) -> Optional[dict]:
        data = self._get_state(symbol)
        if not data:
            return None
        return {
            'acc': self._wss_api.account_name,
            'tb': self.subscription,
            'sch': self._wss_api.schema,
            'act': "partial",
            'd': data
        }
