from __future__ import annotations
from typing import (
    Optional,
    Dict,
    TYPE_CHECKING
)
from ....wss.router import Router
from ....wss.serializer import Serializer
from .utils import parse_message
# from ..utils import stock2symbol
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

        table = data.get('e') if isinstance(data, dict) else data[0].get('e')
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
        self._routed_data[subscr_name] = {
            'table': table,
            'action': 'update',
            'data': list()
        }
        serializer = self._subscr_serializer(subscr_name)
        symbol = data['s'] if isinstance(data, dict) else None
        if self._wss_api.is_registered(subscr_name, symbol) \
           and serializer.is_item_valid(data, {}):
            self._routed_data[subscr_name]['data'].append(data)
        if self._routed_data[subscr_name]['data']:
            return serializer
        return None
