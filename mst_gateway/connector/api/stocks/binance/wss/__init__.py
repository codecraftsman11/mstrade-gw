import asyncio
from logging import Logger
from typing import Optional, Union
from mst_gateway.exceptions import ConnectorError
from websockets import client
from . import subscribers as subscr_class
from .router import BinanceWssRouter, BinanceFuturesWssRouter
from .utils import is_auth_ok, make_cmd
from ..lib import AsyncClient
from ..utils import to_float
from .... import OrderSchema
from ....wss import StockWssApi
from .. import var


class BinanceWssApi(StockWssApi):
    BASE_URL = 'wss://stream.binance.com:9443/ws'
    name = 'binance'
    subscribers = {
        'order_book': subscr_class.BinanceOrderBookSubscriber(),
        'trade': subscr_class.BinanceTradeSubscriber(),
        'quote_bin': subscr_class.BinanceQuoteBinSubscriber(),
        'symbol': subscr_class.BinanceSymbolSubscriber(),
    }

    auth_subscribers = {
        'wallet': subscr_class.BinanceWalletSubscriber(),
        'order': subscr_class.BinanceOrderSubscriber(),
        'position': subscr_class.BinancePositionSubscriber(),
    }
    register_state_groups = [
        'wallet'
    ]

    router_class = BinanceWssRouter
    refresh_key_time = 1800

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 throttle_rate: int = 30,
                 throttle_storage=None,
                 schema='exchange',
                 state_storage=None,
                 register_state=True):
        self.test = self._is_test(url)
        super().__init__(name, account_name, url, auth, logger, options, throttle_rate,
                         throttle_storage, schema, state_storage, register_state)

    def _is_test(self, url):
        return url != self.BASE_URL

    async def _refresh_key(self):
        while True:
            await asyncio.sleep(self.refresh_key_time)
            await self._generate_auth_url()

    async def open(self, **kwargs):
        if kwargs.get('is_auth') or self.auth_connect:
            self.auth_connect = True
            await self._generate_auth_url()
            _task = asyncio.create_task(self._refresh_key())
            self.tasks.append(_task)
        return await super().open(**kwargs)

    async def _generate_auth_url(self):
        key = await self._generate_listen_key()
        self._url = f"{self._url}/{key}"

    async def _generate_listen_key(self):
        if bin_client := await AsyncClient.create(
            api_key=self.auth.get('api_key'), api_secret=self.auth.get('api_secret'), testnet=self.test
        ):
            try:
                if self.schema == OrderSchema.exchange:
                    key = await bin_client.stream_get_listen_key()
                elif self.schema == OrderSchema.margin2:
                    key = await bin_client.margin_stream_get_listen_key()
                elif self.schema == OrderSchema.futures:
                    key = await bin_client.futures_stream_get_listen_key()
                else:
                    raise ConnectorError(f"Invalid schema {self.schema}.")
            except Exception as e:
                raise ConnectorError(e)
            if not key:
                raise ConnectorError(f"Binance api error. Details: Invalid listen key")
            return key

    async def _connect(self, **kwargs):
        kwargs['ws_options'] = {
            'max_size': 2 ** 24,
            'max_queue': 2 ** 7,
            'read_limit': 2 ** 18,
            'write_limit': 2 ** 18,
        }
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        self._logger.info('Binance ws connected successful.')
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        return self.auth_connect

    def get_state(self, subscr_name: str, symbol: str = None) -> Optional[dict]:
        return None

    def _lookup_table(self, message: Union[dict, list]) -> Optional[dict]:
        _message = {
            'table': None,
            'action': 'update',
            'data': []
        }
        if isinstance(message, list) and message and isinstance(message[0], dict):
            table = message[0].get('e')
            _message['table'] = table
            _message['data'].extend(message)
            return _message
        if isinstance(message, dict):
            _message['table'] = message.get('e')
            _message['data'].append(message)
            return _message
        return None

    def __split_message_map(self, key: str) -> Optional[callable]:
        _map = {
            'depthUpdate': self.split_order_book,
            'executionReport': self.split_order,
            'outboundAccountPosition': self.split_wallet,
        }
        return _map.get(key)

    def _split_message(self, message):
        method = self.__split_message_map(message['table'])
        if not method:
            return super(BinanceWssApi, self)._split_message(message)
        return super(BinanceWssApi, self)._split_message(method(message=message))

    def split_order_book(self, message):
        message.pop('action', None)
        _messages = []
        _data_delete = []
        _data_update = []
        for item in message.pop('data', []):
            bids = item.pop('b', [])
            asks = item.pop('a', [])
            for bid in bids:
                if to_float(bid[1]):
                    _data_update.append({'b': bid, **item})
                else:
                    _data_delete.append({'b': bid, **item})
            for ask in asks:
                if to_float(ask[1]):
                    _data_update.append({'a': ask, **item})
                else:
                    _data_delete.append({'a': ask, **item})
            _messages.append(dict(**message, action='delete', data=_data_delete))
            _messages.append(dict(**message, action='update', data=_data_update))
        return _messages

    def split_wallet(self, message):
        subscr_name = self.router_class.table_route_map.get('outboundAccountPosition')
        if subscr_name not in self._subscriptions:
            return None
        if "*" not in self._subscriptions[subscr_name]:
            _balances = []
            _new_data = []
            for item in message.pop('data', []):
                for b in item.pop('B', []):
                    if b['a'].lower() in self._subscriptions[subscr_name]:
                        _balances.append(b)
                item['B'] = _balances
                _new_data.append(item)
            message['data'] = _new_data
        return message

    def split_order(self, message):
        message.pop('action', None)
        _messages = []
        for item in message.pop('data', []):
            action = self.define_action_by_order_status(item.get('X'))
            _messages.append(dict(**message, action=action, data=[item]))
        return _messages

    def define_action_by_order_status(self, order_status: str) -> str:
        if order_status == var.BINANCE_ORDER_STATUS_NEW:
            return 'insert'
        elif order_status in var.BINANCE_ORDER_DELETE_ACTION_STATUSES:
            return 'delete'
        return 'update'


class BinanceFuturesWssApi(BinanceWssApi):
    BASE_URL = 'wss://fstream.binance.com/ws'
    TEST_URL = 'wss://stream.binancefuture.com/ws'

    subscribers = {
        'order_book': subscr_class.BinanceOrderBookSubscriber(),
        'trade': subscr_class.BinanceTradeSubscriber(),
        'quote_bin': subscr_class.BinanceQuoteBinSubscriber(),
        'symbol': subscr_class.BinanceFuturesSymbolSubscriber(),
    }
    auth_subscribers = {
        'wallet': subscr_class.BinanceWalletSubscriber(),
        'order': subscr_class.BinanceOrderSubscriber(),
        'position': subscr_class.BinanceFuturesPositionSubscriber(),
    }

    router_class = BinanceFuturesWssRouter

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 throttle_rate: int = 30,
                 throttle_storage=None,
                 schema='futures',
                 state_storage=None,
                 register_state=True):
        super().__init__(name, account_name, url, auth, logger, options, throttle_rate,
                         throttle_storage, schema, state_storage, register_state)
        self._url = self._generate_url()

    def _is_test(self, url):
        return url != super().BASE_URL

    def _generate_url(self):
        if self.test:
            return self.TEST_URL
        return self.BASE_URL

    def __split_message_map(self, key: str) -> Optional[callable]:
        _map = {
            'depthUpdate': self.split_order_book,
            'ORDER_TRADE_UPDATE': self.split_order,
        }
        return _map.get(key)

    def _split_message(self, message):
        method = self.__split_message_map(message['table'])
        if not method:
            return super(BinanceWssApi, self)._split_message(message)
        return super(BinanceWssApi, self)._split_message(method(message=message))

    def split_order(self, message):
        message.pop('action', None)
        _messages = []
        for item in message.pop('data', []):
            item.update(**item.pop('o', {}))
            action = self.define_action_by_order_status(item.get('X'))
            _messages.append(dict(**message, action=action, data=[item]))
        return _messages
