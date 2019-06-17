from typing import Dict, Set
from abc import ABCMeta, abstractmethod
from logging import Logger
from ...base import Connector
from .. import ERROR_OK
from .channel import StockWssChannel


Route = str
SubscriptionRoutes = Dict[Route, Set[StockWssChannel]]


class StockWssConnector(Connector):
    __metaclass__ = ABCMeta
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = ERROR_OK
        self._subscriptions: Dict[str, SubscriptionRoutes]
        super().__init__(auth, logger)

    def subscirbe(self, subscription: str, wss_channel: StockWssChannel, route: str = ""):
        if not route:
            self._subscribe_root(subscription, wss_channel)
            return
        channelset = self._make_channelset(subscription, route)
        channelset.add(wss_channel)

    def _subscribe_root(self, subscription: str, wss_channel: StockWssChannel):
        pass

    def _make_channelset(self, subscription, route):
        # pylint: disable=no-self-use,unused-argument
        """
        Create channel set
        """
        return set()

    @abstractmethod
    def unsubscribe(self, wss_channel: StockWssChannel, subscription: str,
                    route: str = ""):
        channelset = self._get_channelset(subscription, route)
        if channelset:
            channelset.remove(wss_channel)

    def _get_channelset(self, subscription: str, route: str):
        if subscription not in self._subscriptions:
            return None
        if route not in self._subscriptions[subscription]:
            return None
        return self._subscriptions[subscription][route]
