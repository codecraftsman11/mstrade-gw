import asyncio
from logging import Logger
from typing import Optional, Union
from mst_gateway.exceptions import ConnectorError
from websockets import client
from . import subscribers as subscr_class
from .router import BinanceWssRouter, BinanceMarginWssRouter, BinanceMarginCoinWssRouter
from .utils import is_auth_ok, make_cmd
from .. import rest
from ....wss import StockWssApi, ThrottleWss
from ..utils import to_float, remap_futures_coin_position_request_data
from .... import OrderSchema, ExchangeDrivers
from .. import var


class BinanceWssApi(StockWssApi):
    driver = ExchangeDrivers.binance
    BASE_URL = 'wss://stream.binance.com:9443/ws'
    TEST_URL = 'wss://testnet.binance.vision/ws'
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

    router_class = BinanceWssRouter
    refresh_key_time = 1800
    throttle = ThrottleWss(ws_limit=var.BINANCE_THROTTLE_LIMITS.get('ws'))

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 test: bool = True,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 schema='exchange',
                 state_storage=None,
                 ratelimit=None,
                 register_state=True):
        super().__init__(name, account_name, url, test, auth, logger, options,
                         schema, state_storage, ratelimit, register_state)

        self.listen_key = None

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
        self.listen_key = await self._generate_listen_key()
        self._url = f"{self._url}/{self.listen_key}"

    async def _generate_listen_key(self):
        with rest.BinanceRestApi(
                auth=self.auth, test=self.test, ratelimit=self.ratelimit
        ) as bin_client:
            try:
                if self.schema == OrderSchema.exchange:
                    key = bin_client.handler.stream_get_listen_key()
                elif self.schema == OrderSchema.margin_cross:
                    key = bin_client.handler.margin_stream_get_listen_key()
                elif self.schema == OrderSchema.margin:
                    key = bin_client.handler.futures_stream_get_listen_key()
                elif self.schema == OrderSchema.margin_coin:
                    key = bin_client.handler.futures_coin_stream_get_listen_key()
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
            'max_queue': 2 ** 13,
            'read_limit': 2 ** 18,
            'write_limit': 2 ** 18,
        }
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        self._logger.info(f"{self.__class__.__name__} - schema: {self.schema}, "
                          f"test: {self.test} - connected successful.")
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


class BinanceMarginWssApi(BinanceWssApi):
    BASE_URL = 'wss://fstream.binance.com/ws'
    TEST_URL = 'wss://stream.binancefuture.com/ws'

    subscribers = {
        'order_book': subscr_class.BinanceOrderBookSubscriber(),
        'trade': subscr_class.BinanceTradeSubscriber(),
        'quote_bin': subscr_class.BinanceQuoteBinSubscriber(),
        'symbol': subscr_class.BinanceMarginSymbolSubscriber(),
    }
    auth_subscribers = {
        'wallet': subscr_class.BinanceWalletSubscriber(),
        'order': subscr_class.BinanceOrderSubscriber(),
        'position': subscr_class.BinanceMarginPositionSubscriber(),
    }

    router_class = BinanceMarginWssRouter

    def __init__(self,
                 name: str = None,
                 account_name: str = None,
                 url: str = None,
                 test: bool = True,
                 auth: dict = None,
                 logger: Logger = None,
                 options: dict = None,
                 schema=OrderSchema.margin,
                 state_storage=None,
                 ratelimit=None,
                 register_state=True):
        super().__init__(name, account_name, url, test, auth, logger, options,
                         schema, state_storage, ratelimit, register_state)

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


class BinanceMarginCoinWssApi(BinanceMarginWssApi):
    BASE_URL = 'wss://dstream.binance.com/ws'
    TEST_URL = 'wss://dstream.binancefuture.com/ws'

    subscribers = {
        'symbol': subscr_class.BinanceMarginSymbolSubscriber(),
        'quote_bin': subscr_class.BinanceQuoteBinSubscriber(),
        'trade': subscr_class.BinanceTradeSubscriber(),
        'order_book': subscr_class.BinanceOrderBookSubscriber(),
    }
    auth_subscribers = {
        'wallet': subscr_class.BinanceWalletSubscriber(),
        'order': subscr_class.BinanceOrderSubscriber(),
        'position': subscr_class.BinanceMarginCoinPositionSubscriber(),
    }

    router_class = BinanceMarginCoinWssRouter

    def _lookup_table(self, message: Union[dict, list]) -> Optional[dict]:
        if isinstance(message, dict) and message.get('result'):
            try:
                result = message.get('result', [])[0]
                table = result.get('req', []).split('@')[1]
            except IndexError:
                return None
            _message = {
                'table': table,
                'action': 'update',
                'data': []
            }
            if data := result.get('res', {}).get('positions', []):
                _message['data'] = data
            return _message
        return super()._lookup_table(message)

    def _split_position(self, message: dict) -> list:
        _messages = []
        for position in message.pop('data', []):
            if position.get('positionSide', '') == var.BinancePositionSideMode.BOTH:
                _messages.append(dict(**message, data=[
                    remap_futures_coin_position_request_data(position)
                ]))
        return _messages

    def __split_message_map(self, key: str) -> Optional[callable]:
        _map = {
            'position': self._split_position,
        }
        return _map.get(key)

    def _split_message(self, message):
        method = self.__split_message_map(message['table'])
        if not method:
            return super()._split_message(message)
        return super(BinanceWssApi, self)._split_message(method(message=message))
