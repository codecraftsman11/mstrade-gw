from typing import Dict
from abc import ABCMeta
from abc import abstractmethod
from logging import Logger
from ...base import Connector
from .. import errors
from .subscription import Subscription
from .router import Router
from .serializer import Serializer


class StockWssApi(Connector):
    __metaclass__ = ABCMeta
    subscriptions: Dict[str, Subscription] = {
        'symbol': None,
        'quote': None,
        'quote_bin': None
    }
    BASE_URL = None

    def __init__(self, url: str = None, auth: dict = None, logger: Logger = None):
        self._url: str = url if url is not None else self.__class__.BASE_URL
        self._error: tuple = errors.ERROR_OK
        self._router: Router = self._create_router()
        super().__init__(auth, logger)

    def subscription(self, subscr_name: str) -> Subscription:
        return self.__class__.subscriptions.get(subscr_name)

    def get_message(self, message: dict) -> Serializer:
        serializer = self._router.get(message)
        if not serializer:
            return None
        if not serializer.is_valid():
            self._error = errors.ERROR_INVALID_DATA
            self._logger.error("Error validating incoming message %s", message)
            return None
        return serializer.validated_data

    @abstractmethod
    def _create_router(self) -> Router:
        """
        return new router instance
        """
