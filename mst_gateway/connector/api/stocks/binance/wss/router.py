from __future__ import annotations
from typing import (
    Optional,
    Dict,
    TYPE_CHECKING
)
from ....wss.router import Router
from ....wss.serializer import Serializer
from . import serializers
from .serializers.base import BinanceSerializer


if TYPE_CHECKING:
    from . import BinanceWssApi


class BinanceWssRouter(Router):
    table_route_map = {
        'trade': 'trade',
        'depthUpdate': 'order_book',
        'kline': 'quote_bin',
        '24hrTicker': 'symbol',
        'outboundAccountPosition': 'wallet',
        'executionReport': 'order'
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceSymbolSerializer,
        'wallet': serializers.BinanceWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
    }

    def __init__(self, wss_api: BinanceWssApi):
        self._serializers = {}
        super().__init__(wss_api)

    def _get_serializers(self, message: dict) -> Dict[str, Serializer]:
        self._routed_data = {}
        _serializers = {}
        table = message['table']
        if table not in self.table_route_map:
            return _serializers
        subscriptions = self.table_route_map[table]
        if not isinstance(subscriptions, list):
            subscriptions = [subscriptions]
        for subscr_name in subscriptions:
            serializer = self._lookup_serializer(subscr_name, message)
            if serializer:
                _serializers[subscr_name] = serializer
        return _serializers

    def _subscr_serializer(self, subscr_name) -> BinanceSerializer:
        if subscr_name not in self._serializers:
            self._serializers[subscr_name] = self.serializer_classes[subscr_name](self._wss_api)
        return self._serializers[subscr_name]

    def _lookup_serializer(self, subscr_name, data: dict) -> Optional[BinanceSerializer]:
        serializer = self._subscr_serializer(subscr_name)
        serializer.prefetch(data)
        self._routed_data[subscr_name] = {
            'table': data['table'],
            'action': data['action'],
            'schema': self._wss_api.schema,
            'data': data['data']
        }
        if self._routed_data[subscr_name]['data']:
            return serializer
        return None


class BinanceFuturesWssRouter(BinanceWssRouter):
    table_route_map = {
        'trade': 'trade',
        'depthUpdate': 'order_book',
        'kline': 'quote_bin',
        '24hrTicker': 'symbol',
        'bookTicker': 'symbol',
        'ACCOUNT_UPDATE': 'wallet',
        'ORDER_TRADE_UPDATE': 'order'
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceFuturesSymbolSerializer,
        'wallet': serializers.BinanceFuturesWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
    }
