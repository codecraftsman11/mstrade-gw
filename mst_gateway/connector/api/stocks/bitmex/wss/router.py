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
        'quote_bin_trade': serializers.BitmexQuoteBinFromTradeSerializer,
        'order': serializers.BitmexOrderSerializer
    }

    def __init__(self, wss_api: BitmexWssApi):
        self._serializers = {}
        self._use_trade_bin = bool(wss_api.options.get('use_trade_bin', True))
        if self._use_trade_bin:
            self._quote_bin = 'quote_bin'
        else:
            self._quote_bin = 'quote_bin_trade'
        super().__init__(wss_api)

    def _get_serializer(self, message: str) -> Serializer:
        self._routed_data = None
        data = parse_message(message)
        if self._is_subscription_message(data):
            return self._get_subscription_serializer(data)
        return None

    def _is_subscription_message(self, data: dict) -> bool:
        # pylint: disable=no-self-use
        return 'table' in data and data['action'] in ("partial", "update", "insert")

    def _get_subscription_serializer(self, data: dict) -> Serializer:
        if data['table'] == "instrument":
            return self._lookup_serializer("symbol", data)
        if data['table'] == "trade":
            return self._lookup_serializer("quote_bin", data)
        if data['table'] == "tradeBin1m":
            if self._use_trade_bin or data['action'] == 'partial':
                return self._lookup_serializer("quote_bin", data)
        if data['table'] == "order":
            return self._lookup_serializer("order", data)
        return None

    def _subscr_serializer(self, subscr_name) -> Serializer:
        if subscr_name not in self._serializers:
            subscr_key = self._quote_bin if subscr_name == "quote_bin" else subscr_name
            self._serializers[subscr_name] = self.__class__.serializer_classes[subscr_key](self._wss_api)
        return self._serializers[subscr_name]

    def _lookup_serializer(self, subscr_name, data: list) -> Serializer:
        self._routed_data = {
            'table': data['table'],
            'action': data.get('action'),
            'data': list()
        }
        serializer = self._subscr_serializer(subscr_name)
        for item in data['data']:
            if self._wss_api.is_registered(subscr_name, item['symbol']) \
               and serializer.is_item_valid(data, item):
                self._routed_data['data'].append(item)
        if self._routed_data['data']:
            return serializer
        return None
