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
        'outboundAccountInfo': 'wallet',
        'outboundAccountPosition': 'wallet',
        'executionReport': ['order', 'execution'],
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceSymbolSerializer,
        'wallet': serializers.BinanceWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
        'execution': serializers.BinanceExecutionSerializer,
    }

    def __init__(self, wss_api: BinanceWssApi):
        self._serializers = {}
        super().__init__(wss_api)

    def _get_serializers(self, message: str) -> Dict[str, Serializer]:
        self._routed_data = {}
        _serializers = {}
        data = parse_message(message)
        if isinstance(data, dict):
            table = data.get('e') or self._book_ticker_table(data)
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

    def _book_ticker_table(self, data):
        _table = None
        if {'u', 'E', 'T', 's', 'b', 'B', 'a', 'A'} >= data.keys():
            _table = 'bookTicker'
            data.update({'e': _table})
        return _table

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
        route_key = self._get_route_key(data, subscr_name)
        if self._wss_api.is_registered(subscr_name, route_key) \
           and serializer.is_item_valid(data, {}):
            self._routed_data[subscr_name]['data'].append(data)
        if self._routed_data[subscr_name]['data']:
            return serializer
        return None

    def _get_route_key(self, data, subscr_name):
        if not isinstance(data, dict):
            return None
        if data.get('e') in ('outboundAccountInfo',):
            return None
        if data.get('e') in ('executionReport',):
            table_routes = self.table_route_map.get(data['e'])
            if isinstance(
                self._wss_api.subscriptions.get(table_routes[table_routes.index(subscr_name)]), bool
            ):
                return None
        if data.get('e') in ('outboundAccountPosition',) and data.get('B'):
            try:
                return data['B'][0]['a']
            except (KeyError, IndexError):
                return None
        return data.get('s')


class BinanceFuturesWssRouter(BinanceWssRouter):
    table_route_map = {
        'trade': "trade",
        'depthUpdate': "order_book",
        'kline': "quote_bin",
        '24hrTicker': "symbol",
        'bookTicker': "symbol",
        'ACCOUNT_UPDATE': 'wallet',
        'ORDER_TRADE_UPDATE': ['order', 'execution'],
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceFuturesSymbolSerializer,
        'wallet': serializers.BinanceFuturesWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
        'execution': serializers.BinanceExecutionSerializer,
    }

    def _get_route_key(self, data, subscr_name):
        if not isinstance(data, dict):
            return None
        if data.get('e') in ('ACCOUNT_UPDATE',) and isinstance(
                self._wss_api.subscriptions.get(self.table_route_map.get(data['e'])), dict):
            try:
                return data['a']['B'][0]['a']
            except (KeyError, IndexError):
                return None
        if data.get('e') in ('ORDER_TRADE_UPDATE',):
            table_routes = self.table_route_map.get(data['e'])
            if isinstance(
                self._wss_api.subscriptions.get(table_routes[table_routes.index(subscr_name)]), bool
            ):
                return None
            else:
                try:
                    return data['o']['s']
                except KeyError:
                    pass
            return None
        return data.get('s')
