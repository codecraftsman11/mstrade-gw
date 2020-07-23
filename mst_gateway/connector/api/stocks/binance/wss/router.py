from __future__ import annotations
from typing import (
    Optional,
    Dict,
    TYPE_CHECKING
)
from ....wss.router import Router
from ....wss.serializer import Serializer
from .utils import parse_message
from . import serializers
from .serializers.base import BinanceSerializer


if TYPE_CHECKING:
    from . import BinanceWssApi


class BinanceWssRouter(Router):
    table_route_map = {
        'trade': "trade",
        'depthUpdate': "order_book",
        'kline': "quote_bin",
        '24hrTicker': "symbol",
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceSymbolSerializer,
    }

    def __init__(self, wss_api: BinanceWssApi):
        self._serializers = {}
        super().__init__(wss_api)

    def _get_serializers(self, message: str) -> Dict[str, Serializer]:
        self._routed_data = {}
        _serializers = {}
        data = parse_message(message)
        if isinstance(data, dict):
            table = data.get('e')
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            table = data[0].get('e')
        else:
            return _serializers
        if table not in self.table_route_map:
            return _serializers
        subscriptions = self.table_route_map[table]
        if not isinstance(subscriptions, list):
            subscriptions = [subscriptions]
        for subscr_name in subscriptions:
            serializer = self._lookup_serializer(subscr_name, data, table)
            if serializer:
                _serializers[subscr_name] = serializer
        return _serializers

    def _subscr_serializer(self, subscr_name) -> BinanceSerializer:
        if subscr_name not in self._serializers:
            subscr_key = subscr_name
            self._serializers[subscr_name] = self.__class__.serializer_classes[subscr_key](self._wss_api)
        return self._serializers[subscr_name]

    def _lookup_serializer(self, subscr_name, data: dict, table) -> Optional[Serializer]:
        action = data.get('action', 'update') if isinstance(data, dict) else 'update'
        self._routed_data[subscr_name] = {
            'table': table,
            'action': action,
            'schema': self._wss_api.schema,
            'data': list()
        }
        serializer = self._subscr_serializer(subscr_name)
        symbol = data.get('s') if isinstance(data, dict) else None
        if self._wss_api.is_registered(subscr_name, symbol) \
           and serializer.is_item_valid(data, {}):
            self._routed_data[subscr_name]['data'].append(data)
        if self._routed_data[subscr_name]['data']:
            return serializer
        return None


class BinanceFuturesWssRouter(BinanceWssRouter):
    pass
