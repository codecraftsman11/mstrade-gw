from __future__ import annotations
from typing import (
    Optional,
    Dict,
    TYPE_CHECKING
)
from . import serializers
from .serializers.base import BitmexSerializer
from .utils import parse_message
from ..utils import stock2symbol
from ....wss.router import Router
from ....wss.serializer import Serializer

if TYPE_CHECKING:
    from . import BitmexWssApi


class BitmexWssRouter(Router):
    table_route_map = {
        'instrument': "symbol",
        'trade': ["quote_bin", "trade"],
        'tradeBin1m': "quote_bin",
        'order': "order",
        'orderBookL2_25': "order_book",
        'position': 'position',
        'execution': 'execution',
        'margin': 'wallet'
    }

    serializer_classes = {
        'symbol': serializers.BitmexSymbolSerializer,
        'quote_bin': serializers.BitmexQuoteBinSerializer,
        'quote_bin_trade': serializers.BitmexQuoteBinFromTradeSerializer,
        'order_book': serializers.BitmexOrderBookSerializer,
        'order': serializers.BitmexOrderSerializer,
        'trade': serializers.BitmexTradeSerializer,
        'position': serializers.BitmexPositionSerializer,
        'execution': serializers.BitmexExecutionSerializer,
        'wallet': serializers.BitmexWalletSerializer
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

    def _get_serializers(self, message: str) -> Dict[str, Serializer]:
        self._routed_data = {}
        _serializers = {}
        data = parse_message(message)
        if not self._is_subscription_message(data):
            return _serializers
        if data['table'] not in self.table_route_map:
            return _serializers
        subscriptions = self.table_route_map[data['table']]
        if not isinstance(subscriptions, list):
            subscriptions = [subscriptions]
        for subscr_name in subscriptions:
            serializer = self._lookup_serializer(subscr_name, data)
            if serializer:
                _serializers[subscr_name] = serializer
        return _serializers

    def _is_subscription_message(self, data: dict) -> bool:
        # pylint: disable=no-self-use
        return 'table' in data and data['action'] in ("partial", "update",
                                                      "insert", "delete")

    def _subscr_serializer(self, subscr_name) -> BitmexSerializer:
        if subscr_name not in self._serializers:
            subscr_key = self._quote_bin if subscr_name == "quote_bin" else subscr_name
            self._serializers[subscr_name] = self.__class__.serializer_classes[subscr_key](self._wss_api)
        return self._serializers[subscr_name]

    def _lookup_serializer(self, subscr_name, data: dict) -> Optional[Serializer]:
        table = data['table']
        if table == "tradeBin1m":
            if not self._use_trade_bin and data['action'] != 'partial':
                return None
        self._routed_data[subscr_name] = {
            'table': table,
            'action': data.get('action'),
            'schema': self._wss_api.schema,
            'data': list()
        }
        serializer = self._subscr_serializer(subscr_name)
        for item in data['data']:
            route_key = self._get_route_key(item, subscr_name)
            if self._wss_api.is_registered(subscr_name, stock2symbol(route_key)) \
               and serializer.is_item_valid(data, item):
                self._routed_data[subscr_name]['data'].append(item)
        if self._routed_data[subscr_name]['data']:
            return serializer
        return None

    def _get_route_key(self, data, subscr_name):
        if isinstance(self._wss_api.subscriptions.get(subscr_name), bool):
            return None
        return data.get('currency') or data.get('symbol')
