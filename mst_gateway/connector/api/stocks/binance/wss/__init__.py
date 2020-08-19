import asyncio
import json
from logging import Logger
from typing import Optional, Union
from mst_gateway.exceptions import ConnectorError
from websockets import client
from . import subscribers as subscr
from .router import BinanceWssRouter, BinanceFuturesWssRouter
from .utils import is_auth_ok, make_cmd, parse_message
from ..lib import Client
from ..utils import to_float
from .... import errors
from ....wss import StockWssApi


class BinanceWssApi(StockWssApi):
    BASE_URL = 'wss://stream.binance.com:9443/ws'
    name = 'binance'
    subscribers = {
        'order_book': subscr.BinanceOrderBookSubscriber(),
        'trade': subscr.BinanceTradeSubscriber(),
        'quote_bin': subscr.BinanceQuoteBinSubscriber(),
        'symbol': subscr.BinanceSymbolSubscriber()
    }

    auth_subscribers = {
        'wallet': subscr.BinanceWalletSubscriber()
    }

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
                 state_storage=None):
        self.test = self._is_test(url)
        super().__init__(name, account_name, url, auth, logger, options, throttle_rate,
                         throttle_storage, schema, state_storage)

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
            asyncio.create_task(self._refresh_key())
        return await super().open()

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

    async def process_message(self, message, on_message: Optional[callable] = None):
        messages = self._split_message(message)
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            try:
                data = self.get_data(message)
            except Exception as exc:
                self._error = errors.ERROR_INVALID_DATA
                self._logger.error("Error validating incoming message %s; Details: %s", message, exc)
                continue
            if not data:
                continue
            if on_message:
                if asyncio.iscoroutinefunction(on_message):
                    await on_message(data)
                else:
                    on_message(data)
        return None

    def _split_message(self, message):
        message = self.split_order_book(message)
        return message

    def split_order_book(self, message) -> Union[str, list]:
        data = parse_message(message)
        if isinstance(data, list) or (isinstance(data, dict) and data.get('e') != 'depthUpdate'):
            return message
        bids = data.pop('b')
        asks = data.pop('a')
        bid_u, bid_d = list(), list()
        ask_u, ask_d = list(), list()
        for bid in bids:
            bid_d.append(bid) if to_float(bid[1]) else bid_u.append(bid)
        for ask in asks:
            ask_d.append(ask) if to_float(ask[1]) else ask_u.append(ask)
        messages = [
            json.dumps(dict(b=bid_d, a=ask_d, action='delete', **data)),
            json.dumps(dict(b=bid_u, a=ask_u, action='update', **data))
        ]
        return messages


class BinanceFuturesWssApi(BinanceWssApi):
    BASE_URL = 'wss://fstream.binance.com/ws'
    TEST_URL = 'wss://stream.binancefuture.com/ws'
    name = 'binance'
    subscribers = {
        'order_book': subscr.BinanceOrderBookSubscriber(),
        'trade': subscr.BinanceTradeSubscriber(),
        'quote_bin': subscr.BinanceQuoteBinSubscriber(),
        'symbol': subscr.BinanceSymbolSubscriber()
    }

    auth_subscribers = {
        'wallet': subscr.BinanceWalletSubscriber()
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
                 state_storage=None):
        super().__init__(name, account_name, url, auth, logger, options,
                         throttle_rate, throttle_storage, schema, state_storage)
        self._url = self._generate_url()

    def _is_test(self, url):
        return url != super().BASE_URL

    def _generate_url(self):
        if self.test:
            return self.TEST_URL
        return self.BASE_URL

    def _split_message(self, message):
        message = self.split_wallet(message)
        return super()._split_message(message)

    def split_wallet(self, message) -> Union[str, list]:
        data = parse_message(message)
        if data.get('e') != 'ACCOUNT_UPDATE':
            return message
        if isinstance(self._subscriptions.get('wallet'), dict):
            message = list()
            balances = data.get('a').pop('B')
            for asset in self._subscriptions.get('wallet').keys():
                for b in balances:
                    if b.get('a', '').lower() == asset:
                        data['a']['B'] = [b]
                        message.append(json.dumps(data))
        return message
