from __future__ import annotations
from typing import TYPE_CHECKING
from ....wss.router import Router
from ....wss.serializer import Serializer
from .utils import parse_message
from ..utils import stock2symbol
from . import serializers


if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexWssRouter(Router):
    table_route_map = {
        'instrument': "symbol",
        'trade': "quote_bin",
        'tradeBin1m': "quote_bin",
        'order': "order",
        'orderBookL2_25': "order_book"
    }

    serializer_classes = {
        'symbol': serializers.BitmexSymbolSerializer,
        'quote_bin': serializers.BitmexQuoteBinSerializer,
        'quote_bin_trade': serializers.BitmexQuoteBinFromTradeSerializer,
        'order_book': serializers.BitmexOrderBookSerializer,
        'order': serializers.BitmexOrderSerializer
    }

    def __init__(self, wss_api: BitmexWssApi):
        self._serializers = {}
        self._use_trade_bin = bool(wss_api.options.get('use_trade_bin', True))
        if self._use_trade_bin:
            # use periodical quote_bin change events
            self._quote_bin = 'quote_bin'
        else:
            # use realtime quote change events
            self._quote_bin = 'quote_bin_trade'
        super().__init__(wss_api)

    def _get_serializer(self, message: str) -> Serializer:
        self._routed_data = None
        data = parse_message(message)
        if not self._is_subscription_message(data):
            return None
        if data['table'] not in self.table_route_map:
            return None
        return self._lookup_serializer(self.table_route_map[data['table']], data)

    def _is_subscription_message(self, data: dict) -> bool:
        # pylint: disable=no-self-use
        return 'table' in data and data['action'] in ("partial", "update",
                                                      "insert", "delete")

    def _subscr_serializer(self, subscr_name) -> Serializer:
        if subscr_name not in self._serializers:
            subscr_key = self._quote_bin if subscr_name == "quote_bin" else subscr_name
            self._serializers[subscr_name] = self.__class__.serializer_classes[subscr_key](self._wss_api)
        return self._serializers[subscr_name]

    def _lookup_serializer(self, subscr_name, data: list) -> Serializer:
        if data['table'] == "tradeBin1m":
            if not self._use_trade_bin and data['action'] != 'partial':
                return None
        self._routed_data = {
            'table': data['table'],
            'action': data.get('action'),
            'data': list()
        }
        serializer = self._subscr_serializer(subscr_name)
        for item in data['data']:

            if self._wss_api.is_registered(subscr_name, stock2symbol(item['symbol'])) \
               and serializer.is_item_valid(data, item):
                self._routed_data['data'].append(item)
        if self._routed_data['data']:
            return serializer
        return None
