import json
import time
from websockets import client
from ....wss import StockWssApi
from ....wss.subscriber import Subscriber
from . import subscribers as subscr
from .utils import is_auth_ok, make_cmd, parse_message
from ..lib import bitmex_signature
from .router import BitmexWssRouter
from .... import errors
import asyncio
from typing import Optional


BITMEX_WSS_DEFAULT_TIMEOUT = 5


class BitmexWssApi(StockWssApi):
    BASE_URL = "wss://www.bitmex.com/realtime"
    TEST_URL = "wss://testnet.bitmex.com/realtime"
    name = "bitmex"
    subscribers = {
        'symbol': subscr.BitmexSymbolSubscriber(),
        'quote_bin': subscr.BitmexQuoteBinSubscriber(),
        'order_book': subscr.BitmexOrderBookSubscriber(),
        # 'trade': subscr.BitmexTradeSubscriber()
    }

    auth_subscribers = {
        'order': subscr.BitmexOrderSubscriber(),
        'position': subscr.BitmexPositionSubscriber(),
        'execution': subscr.BitmexExecutionSubscriber(),
        'wallet': subscr.BitmexWalletSubscriber()
    }

    router_class = BitmexWssRouter

    async def _connect(self, **kwargs):
        _ws: client.WebSocketClientProtocol = await super()._connect(**kwargs)
        res = await _ws.recv()
        self._logger.info(res)
        return _ws

    async def authenticate(self, auth: dict = None) -> bool:
        if auth is None:
            auth = self._auth
        wss = self.handler
        expires = int(time.time()) + self._options.get('timeout', BITMEX_WSS_DEFAULT_TIMEOUT)
        signature = bitmex_signature(auth.get('api_secret', ""), "GET", "/realtime", expires)
        await wss.send(make_cmd('authKeyExpires', [auth.get('api_key', ""), expires,
                                                   signature]))
        self.auth_connect = is_auth_ok(await wss.recv())
        return self.auth_connect

    async def process_message(self, message, on_message: Optional[callable] = None):
        messages = self.split_wallet(message)
        if not isinstance(messages, list):
            messages = [messages]
        for message in messages:
            try:
                data = self.get_data(message)
            except Exception as exc:
                self._error = errors.ERROR_INVALID_DATA
                self._logger.error("Error validating incoming message %s; Details: %s", message, exc)
                return None
            if not data:
                return None
            if on_message:
                if asyncio.iscoroutinefunction(on_message):
                    return await on_message(data)
                return on_message(data)
            return data

    def split_wallet(self, message):
        data = parse_message(message)
        if data.get('table') != 'margin':
            return message
        if isinstance(self._subscriptions.get('wallet'), dict):
            message = list()
            for asset, _ in self._subscriptions.get('wallet').items():
                for d in data.pop('data'):
                    if d.get('currency', '').lower() == asset:
                        message.append(json.dumps(dict(data=[d], **data)))
        return message

    def _get_subscriber(self, subscr_name: str) -> Subscriber:
        if subscr_name.lower() == "trade":
            return super()._get_subscriber("quote_bin")
        return super()._get_subscriber(subscr_name)
