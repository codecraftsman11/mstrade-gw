import asyncio
from logging import Logger
from typing import Optional
from mst_gateway.exceptions import ConnectorError
from websockets import client
from . import subscribers as subscr
from .router import BinanceWssRouter, BinanceFuturesWssRouter
from .utils import is_auth_ok, make_cmd, parse_message, dump_message
from ..lib import Client
from ..utils import to_float
from .... import errors
from ....wss import StockWssApi
from .. import var


class BinanceWssApi(StockWssApi):
    BASE_URL = 'wss://stream.binance.com:9443/ws'
    name = 'binance'
    subscribers = {
        'order_book': subscr.BinanceOrderBookSubscriber(),
        'trade': subscr.BinanceTradeSubscriber(),
        'quote_bin': subscr.BinanceQuoteBinSubscriber(),
        'symbol': subscr.BinanceSymbolSubscriber(),
    }

    auth_subscribers = {
        'wallet': subscr.BinanceWalletSubscriber(),
        'order': subscr.BinanceOrderSubscriber(),
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
            self._generate_auth_url()

    async def open(self, **kwargs):
        if kwargs.get('is_auth') or self.auth_connect:
            self.auth_connect = True
            self._generate_auth_url()
            _task = asyncio.create_task(self._refresh_key())
            self.tasks.append(_task)
        return await super().open(**kwargs)

    def _generate_auth_url(self):
        key = self._generate_listen_key()
        self._url = f"{self._url}/{key}"

    def _generate_listen_key(self):
        bin_client = Client(api_key=self.auth.get('api_key'), api_secret=self.auth.get('api_secret'), test=self.test)
        if self.schema == 'exchange':
            key = bin_client.stream_get_listen_key()
        elif self.schema == 'margin2':
            key = bin_client.margin_stream_get_listen_key()
        elif self.schema == 'futures':
            key = bin_client.futures_stream_get_listen_key()
        else:
            raise ConnectorError(f"Invalid schema {self.schema}.")
        if not key:
            raise ConnectorError(f"Binance api error. Details: Invalid listen key")
        return key

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        self._logger.info('Binance ws connected successful.')
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        return self.auth_connect

    def get_state(self, subscr_name: str, symbol: str = None) -> Optional[dict]:
        return None

    def register(self, subscr_name: str, channel: str, symbol: str = None) -> None:
        if self.register_state and subscr_name in self.register_state_groups:
            self.storage.set(f'{subscr_name}.{self.account_name}'.lower(), {'*': '*'})
        return super().register(subscr_name, channel, symbol)

    def unregister(self, subscr_name: str, channel: str, symbol: str = None) -> None:
        if self.register_state and subscr_name in self.register_state_groups:
            self.storage.remove(f'{subscr_name}.{self.account_name}'.lower())
        return super().unregister(subscr_name, channel, symbol)

    def _split_message(self, message):
        data = parse_message(message)
        for method in (
            self.split_order_book,
            self.split_order,
            self.split_wallet
        ):
            _tmp = method(data)
            if _tmp:
                return _tmp
        return message

    def split_order_book(self, data):
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'depthUpdate'):
            return None
        bids = data.pop('b')
        asks = data.pop('a')
        bid_u, bid_d = list(), list()
        ask_u, ask_d = list(), list()
        for bid in bids:
            bid_d.append(bid) if to_float(bid[1]) else bid_u.append(bid)
        for ask in asks:
            ask_d.append(ask) if to_float(ask[1]) else ask_u.append(ask)
        _data = [
            dump_message(dict(b=bid_d, a=ask_d, action='delete', **data)),
            dump_message(dict(b=bid_u, a=ask_u, action='update', **data))
        ]
        return _data

    def split_wallet(self, data):
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'outboundAccountPosition'):
            return None
        if self._subscriptions.get('wallet', dict()).keys() != ["*"]:
            _data = list()
            balances = data.pop('B')
            for b in balances:
                if b.get('a', '').lower() in self._subscriptions['wallet'].keys():
                    data['B'] = [b]
                    _data.append(dump_message(data))
            return _data

    def define_action_by_order_status(self, order_status: str) -> str:
        if order_status == var.BINANCE_ORDER_STATUS_NEW:
            return 'insert'
        elif order_status in var.BINANCE_ORDER_DELETE_ACTION_STATUSES:
            return 'delete'
        return 'update'

    def split_order(self, data):
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'executionReport'):
            return None
        action = self.define_action_by_order_status(data.get('X'))
        return dump_message(dict(action=action, **data))


class BinanceFuturesWssApi(BinanceWssApi):
    BASE_URL = 'wss://fstream.binance.com/ws'
    TEST_URL = 'wss://stream.binancefuture.com/ws'

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
        super().__init__(name, account_name, url, auth, logger, options,
                         throttle_rate, throttle_storage, schema, state_storage, register_state)
        self._url = self._generate_url()

    def _is_test(self, url):
        return url != super().BASE_URL

    def _generate_url(self):
        if self.test:
            return self.TEST_URL
        return self.BASE_URL

    def split_wallet(self, data):
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'ACCOUNT_UPDATE'):
            return None
        if self._subscriptions.get('wallet', dict()).keys() != ["*"]:
            _data = list()
            balances = data.get('a').pop('B')
            for b in balances:
                if b.get('a', '').lower() in self._subscriptions['wallet'].keys():
                    data['a']['B'] = [b]
                    _data.append(dump_message(data))
            return _data

    def split_order(self, data):
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'ORDER_TRADE_UPDATE'):
            return None
        action = self.define_action_by_order_status(data.get('o', dict()).get('X'))
        return dump_message(dict(action=action, **data))
