from __future__ import annotations
from typing import Dict, Optional
from ....wss.router import Router
from ....wss.serializer import Serializer
from . import serializers


class BinanceWssRouter(Router):
    table_route_map = {
        'trade': 'trade',
        'depthUpdate': 'order_book',
        'kline': 'quote_bin',
        '24hrTicker': ['symbol', 'position'],
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
        'position': serializers.BinancePositionSerializer,
    }

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

    def _lookup_serializer(self, subscr_name, data: dict) -> Optional[Serializer]:
        if subscr_name not in self._wss_api.subscriptions:
            return None
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
        'ACCOUNT_UPDATE': ['wallet', 'position'],
        'ORDER_TRADE_UPDATE': 'order',
        'markPriceUpdate': ['position', 'symbol'],
        'ACCOUNT_CONFIG_UPDATE': 'position',
    }

    serializer_classes = {
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'symbol': serializers.BinanceFuturesSymbolSerializer,
        'wallet': serializers.BinanceFuturesWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
        'position': serializers.BinanceFuturesPositionSerializer,
    }


class BinanceFuturesCoinWssRouter(BinanceWssRouter):
    table_route_map = {
        '24hrTicker': 'symbol',
        'bookTicker': 'symbol',
        'kline': 'quote_bin',
        'trade': 'trade',
        'depthUpdate': 'order_book',
        'ACCOUNT_UPDATE': ['wallet', 'position'],
        'ORDER_TRADE_UPDATE': 'order',
        'markPriceUpdate': ['position', 'symbol'],
        'position': 'position'
    }

    serializer_classes = {
        'symbol': serializers.BinanceFuturesSymbolSerializer,
        'quote_bin': serializers.BinanceQuoteBinSerializer,
        'trade': serializers.BinanceTradeSerializer,
        'order_book': serializers.BinanceOrderBookSerializer,
        'wallet': serializers.BinanceFuturesWalletSerializer,
        'order': serializers.BinanceOrderSerializer,
        'position': serializers.BinanceFuturesCoinPositionSerializer
    }
