from __future__ import annotations
from typing import TYPE_CHECKING
from ....wss.router import Router
from ....wss.serializer import Serializer
from .utils import parse_message
from . import serializers


if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexWssRouter(Router):
    serializer_classes = {
        'symbol': serializers.BitmexSymbolSerializer,
        'quote_bin': serializers.BitmexQuoteBinSerializer,
        'order': serializers.BitmexOrderSerializer
    }

    def _get_serializer(self, wss_api: BitmexWssApi, message: str) -> Serializer:
        data = parse_message(message)
        if self._is_subscription_message(data):
            return self._get_subscription_serializer(wss_api, data)
        return None

    def _is_subscription_message(self, data: dict) -> bool:
        # pylint: disable=no-self-use
        return 'table' in data and data.get('action') == "update"

    def _get_subscription_serializer(self, wss_api: BitmexWssApi, data: dict) -> Serializer:
        if data['table'] == "instrument":
            return self._lookup_serializer(wss_api, "symbol", data['data'])
        if data['table'] == "trade" or data['table'] == "tradeBin1m":
            return self._lookup_serializer(wss_api, "quote_bin", data['data'])
        if data['table'] == "order":
            return self._lookup_serializer(wss_api, "order", data['data'])
        return None

    def _lookup_serializer(self, wss_api: BitmexWssApi, subscr_name, data: list) -> Serializer:
        for item in data:
            if wss_api.subscription_registered(subscr_name, item['symbol']) \
               and self.__class__.serializer_classes[subscr_name].is_item_valid(item):
                return self.__class__.serializer_classes[subscr_name](wss_api, data)
        return None
