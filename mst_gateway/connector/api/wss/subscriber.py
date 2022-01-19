from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
from mst_gateway.exceptions import QueryError


if TYPE_CHECKING:
    from . import StockWssApi


class Subscriber:
    __metaclass__ = ABCMeta
    subscription = "base"
    subscriptions = ()
    general_subscribe_available = True
    detail_subscribe_available = True
    is_close_connection = True

    def __init__(self):
        pass

    async def subscribe(self, api: StockWssApi, symbol=None):
        try:
            api.partial_state_data.setdefault(self.subscription, {}).update(await self.init_partial_state(api))
        except Exception:
            return False
        return await self._subscribe(api, symbol)

    async def unsubscribe(self, api: StockWssApi, symbol=None):
        return await self._unsubscribe(api, symbol)

    @abstractmethod
    async def _subscribe(self, api: StockWssApi, symbol=None):
        pass

    @abstractmethod
    async def _unsubscribe(self, api: StockWssApi, symbol=None):
        pass

    async def init_partial_state(self, api: StockWssApi):
        return {}

    async def request(self, api: StockWssApi, channel_name):
        return
