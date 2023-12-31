import asyncio
import json
import pytest
import logging
from copy import deepcopy
from typing import Optional
from schema import Schema
from websockets.exceptions import ConnectionClosed
from mst_gateway.logging import init_logger
from mst_gateway.connector.api.stocks.bitmex.wss import subscribers as subscr_class
from mst_gateway.connector.api.stocks.bitmex import var
from mst_gateway.storage import StateStorageKey
from tests.mst_gateway.connector import schema as fields
from mst_gateway.connector.api import OrderSchema
from mst_gateway.connector.api.stocks.bitmex import BitmexWssApi
import tests.config as cfg
from .data import storage
from . import data as test_data


BITMEX_SYMBOL = 'XBTUSD'


def rest_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_AUTH_KEYS, [OrderSchema.margin])
    }
    return name_map[name]


def wss_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_AUTH_KEYS, OrderSchema.margin)
    }
    return name_map[name]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


@pytest.fixture(params=['tbitmex'])
async def wss(request, _debug) -> BitmexWssApi:
    param = request.param
    test, auth, schema = wss_params(param)
    with BitmexWssApi(
            test=test,
            name='tbitmex',
            auth=auth,
            schema=schema,
            url=cfg.BITMEX_WSS_URL,
            state_storage=deepcopy(storage.STORAGE_DATA),
            logger=_debug['logger']
    ) as wss:
        await wss.open()
        yield wss
        await wss.close()


class TestBitmexWssApi:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss', ['tbitmex'],
        indirect=True,
    )
    async def test_authenticate(self, wss: BitmexWssApi):
        assert not wss.auth_connect
        await wss.authenticate()
        assert wss.auth_connect

    @pytest.mark.parametrize(
        'wss, subscr_name, expect', [
            ('tbitmex', 'symbol', subscr_class.BitmexSymbolSubscriber),
            ('tbitmex', 'quote_bin', subscr_class.BitmexQuoteBinSubscriber),
            ('tbitmex', 'order_book', subscr_class.BitmexOrderBookSubscriber),
            ('tbitmex', 'trade', subscr_class.BitmexTradeSubscriber),
            ('tbitmex', 'order', subscr_class.BitmexOrderSubscriber),
            ('tbitmex', 'position', subscr_class.BitmexPositionSubscriber),
            ('tbitmex', 'wallet', subscr_class.BitmexWalletSubscriber),
        ],
        indirect=['wss'],
    )
    def test__get_subscriber(self, wss: BitmexWssApi, subscr_name: str, expect):
        subscriber = wss._get_subscriber(subscr_name)
        assert isinstance(subscriber, expect)
        assert subscriber.subscription == subscr_name

    @pytest.mark.parametrize(
        'wss, subscr_name, subscriptions, expect', [
            (
                'tbitmex',
                'symbol',
                {"symbol": {BITMEX_SYMBOL.lower(): {"1"}, "*": {"1"}}},
                {"symbol": {"*": {"1"}}},
            ),
            (
                'tbitmex',
                'symbol',
                {"symbol": {BITMEX_SYMBOL.lower(): {"1"}, "*": {"2"}}},
                {"symbol": {"*": {"1", "2"}}},
            ),
        ],
        indirect=['wss'],
    )
    def test_remap_subscriptions(self, wss: BitmexWssApi,
                                 subscr_name: str, subscriptions: dict, expect: dict):
        wss._subscriptions = subscriptions
        assert wss.remap_subscriptions(subscr_name) is None
        assert wss.subscriptions == expect

    @pytest.mark.parametrize(
        'wss, subscr_channel, subscr_name, symbol, expect', [
            ('tbitmex', 'order', 'order', BITMEX_SYMBOL, (True, BITMEX_SYMBOL.lower())),
            ('tbitmex', None, '', BITMEX_SYMBOL, (True, BITMEX_SYMBOL.lower())),
            ('tbitmex', 'trade', '', None, (True, '*')),
        ],
        indirect=['wss'],
    )
    def test_register(self, wss: BitmexWssApi, subscr_channel: Optional[str],
                      subscr_name: str, symbol: Optional[str], expect: bool):
        assert wss.register(subscr_channel, subscr_name, symbol) == expect

    @pytest.mark.parametrize(
        'wss, subscr_channel, subscr_name, symbol, register, expect', [
            ('tbitmex', 'order', '*', None, False, False),
            ('tbitmex', 'order', 'order', BITMEX_SYMBOL, True, True),
            ('tbitmex', 'order', 'order', None, True, True),
        ],
        indirect=['wss'],
    )
    def test_is_registered(self, wss: BitmexWssApi, subscr_channel: Optional[str], subscr_name: str, register: bool,
                           symbol: Optional[str], expect: bool):
        if register:
            wss.register(subscr_channel, subscr_name, symbol)
        assert wss.is_registered(subscr_name, symbol) == expect
        wss.unregister(subscr_channel, subscr_name, symbol)

    @pytest.mark.parametrize(
        'wss, subscr_channel, subscr_name, symbol, register, expect', [
            ('tbitmex', 'order', 'order', BITMEX_SYMBOL, True, (True, BITMEX_SYMBOL.lower())),
            ('tbitmex', None, '', BITMEX_SYMBOL, True, (True, BITMEX_SYMBOL.lower())),
            ('tbitmex', 'trade', '', None, True, (True, '*')),
            ('tbitmex', 'trade', 'trad3', '*', False, (False, '*')),
            ('tbitmex', 'trade', '', None, False, (False, None)),
        ],
        indirect=['wss'],
    )
    def test_unregister(self, wss: BitmexWssApi, subscr_channel: Optional[str], subscr_name: str, register: bool,
                        symbol: Optional[str], expect: bool):
        if register:
            wss.register(subscr_channel, subscr_name, symbol)
        assert wss.unregister(subscr_channel, subscr_name, symbol) == expect

    @pytest.mark.parametrize(
        'wss, subscr_channel, subscr_name, symbol, register, expect', [
            ('tbitmex', 'order', '*', None, False, True),
            ('tbitmex', 'order', 'order', BITMEX_SYMBOL, True, False),
            ('tbitmex', 'order', 'order', BITMEX_SYMBOL, False, True),
            ('tbitmex', 'order', 'order', None, True, False),
        ],
        indirect=['wss'],
    )
    def test_is_unregistered(self, wss: BitmexWssApi, subscr_channel: Optional[str], subscr_name: str, register: bool,
                             symbol: Optional[str], expect: bool):
        if register:
            wss.register(subscr_channel, subscr_name, symbol)
        assert wss.is_unregistered(subscr_name, symbol) == expect
        wss.unregister(subscr_channel, subscr_name, symbol)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name, default_data', [
            ('tbitmex', 'trade', test_data.DEFAULT_TRADE_DATA[OrderSchema.margin]),
            ('tbitmex', 'symbol', test_data.DEFAULT_SYMBOL_DATA[OrderSchema.margin]),
            ('tbitmex', 'order_book', test_data.DEFAULT_ORDER_BOOK_DATA[OrderSchema.margin]),
            ('tbitmex', 'order', test_data.DEFAULT_ORDER_DATA[OrderSchema.margin]),
            ('tbitmex', 'position', test_data.DEFAULT_POSITION_DATA[OrderSchema.margin]),
            ('tbitmex', 'wallet', test_data.DEFAULT_WALLET_DATA[OrderSchema.margin])
        ],
        indirect=['wss']
    )
    async def test_get_data(self, wss: BitmexWssApi, subscr_name: str, default_data: list):
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        message_header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        d_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
        for data in default_data:
            message = json.loads(data['message'])
            wss_data = await wss.get_data(deepcopy(message))
            _data = wss_data[subscr_name]
            assert message_header_schema.validate(_data) == _data
            for d in _data['d']:
                assert d_schema.validate(d) == d
            assert _data == data['expect'][subscr_name]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, default_data', [('tbitmex', test_data.DEFAULT_QUOTE_BIN_DATA[OrderSchema.margin])],
        indirect=['wss']
    )
    async def test_get_quote_bin_data(self, wss: BitmexWssApi, default_data: list):
        subscr_name = 'quote_bin'
        previous_quote_bin_clp = None
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        message_header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        d_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
        for data in default_data:
            message = json.loads(data['message'])
            wss_data = await wss.get_data(message)
            _data = wss_data[subscr_name]
            assert message_header_schema.validate(_data) == _data
            for d in _data['d']:
                assert d_schema.validate(d) == d
            if message['table'] == 'tradeBin1m':
                if previous_quote_bin_clp:
                    assert _data['d'][0]['opp'] == previous_quote_bin_clp
                previous_quote_bin_clp = _data['d'][-1]['clp']
            assert _data == data['expect'][subscr_name]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name, default_data', [
            ('tbitmex', 'trade', test_data.DEFAULT_TRADE_DATA[OrderSchema.margin]),
            ('tbitmex', 'quote_bin', test_data.DEFAULT_QUOTE_BIN_DATA[OrderSchema.margin]),
            ('tbitmex', 'symbol', test_data.DEFAULT_SYMBOL_DATA[OrderSchema.margin]),
            ('tbitmex', 'order_book', test_data.DEFAULT_ORDER_BOOK_DATA[OrderSchema.margin]),
            ('tbitmex', 'order', test_data.DEFAULT_ORDER_DATA[OrderSchema.margin]),
            ('tbitmex', 'position', test_data.DEFAULT_POSITION_DATA[OrderSchema.margin]),
            ('tbitmex', 'wallet', test_data.DEFAULT_WALLET_DATA[OrderSchema.margin]),
        ],
        indirect=['wss']
    )
    async def test_get_state(self, wss: BitmexWssApi, subscr_name: str, default_data: list):
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        message_header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        d_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
        for data in default_data:
            message = json.loads(data['message'])
            await wss.get_data(deepcopy(message))
            _data = wss.get_state(subscr_name)
            if subscr_name == 'order_book':
                assert _data is None
                break
            assert message_header_schema.validate(_data) == _data
            for d in _data['d']:
                assert d_schema.validate(d) == d

    @pytest.mark.parametrize(
        'wss, symbol', [
            ('tbitmex', BITMEX_SYMBOL),
            ('tbitmex', None),
            ('tbitmex', 'NOOT_IN_STORAGE'),
        ],
        indirect=['wss']
    )
    def test_get_state_data(self, wss: BitmexWssApi, symbol: Optional[str]):
        state = wss.get_state_data(symbol)
        assert state == storage.STORAGE_DATA[f"{StateStorageKey.symbol}.{wss.name}.{wss.schema}"].get((symbol or '').lower())

    @pytest.mark.parametrize(
        'wss, default_data, expect', [
            ('tbitmex', test_data.DEFAULT_ORDER_DATA[OrderSchema.margin],
             test_data.DEFAULT_ORDER_SPLIT_DATA[OrderSchema.margin])
        ],
        indirect=['wss']
    )
    def test_split_order(self, wss: BitmexWssApi, default_data: dict,  expect: list):
        for i, data in enumerate(default_data):
            message = json.loads(data['message'])
            wss_data = wss.split_order(deepcopy(message))
            assert wss_data == expect[i]

    @pytest.mark.parametrize(
        'wss, default_data, expect', [
            ('tbitmex', test_data.DEFAULT_TRADE_DATA[OrderSchema.margin],
             test_data.DEFAULT_TRADE_SPLIT_DATA[OrderSchema.margin])
        ],
        indirect=['wss']
    )
    def test_split_trade(self, wss: BitmexWssApi, default_data: dict, expect: list):
        for i, data in enumerate(default_data):
            message = json.loads(data['message'])
            wss_data = wss.split_trade(deepcopy(message))
            assert wss_data == expect[i]

    @pytest.mark.parametrize(
        'wss, message, expect', [
            ('tbitmex', [{'message': '{"table": null}'}], [[{'table': None}]]),
            ('tbitmex', test_data.DEFAULT_TRADE_DATA[OrderSchema.margin],
             test_data.DEFAULT_TRADE_SPLIT_DATA[OrderSchema.margin]),
            ('tbitmex', test_data.DEFAULT_ORDER_DATA[OrderSchema.margin],
             test_data.DEFAULT_ORDER_SPLIT_DATA[OrderSchema.margin])
        ],
        indirect=['wss']
    )
    def test__split_message(self, wss: BitmexWssApi, message: dict, expect: list):
        for i, data in enumerate(message):
            message = json.loads(data['message'])
            wss_data = wss._split_message(deepcopy(message))
            assert wss_data == expect[i]

    @pytest.mark.parametrize(
        'wss, order_status, expect', [
            ('tbitmex', var.BITMEX_ORDER_STATUS_NEW, 'insert'),
            ('tbitmex', var.BITMEX_ORDER_DELETE_ACTION_STATUSES, 'delete'),
            ('tbitmex', ('PendingNew', 'PendingReplace', 'DoneForDay'), 'update'),
        ],
        indirect=['wss']
    )
    def test_define_action_by_order_status(self, wss: BitmexWssApi, order_status, expect: str):
        if isinstance(order_status, str):
            assert wss.define_action_by_order_status(order_status) == expect
        else:
            for os in order_status:
                assert wss.define_action_by_order_status(os) == expect


class TestSubscriptionBitmexWssApi:

    def reset(self):
        self.messages = []

    def on_message(self, data):
        self.messages.append(data)

    async def consume(self, wss, handler, on_message: callable):
        while True:
            try:
                message = await handler.recv()
                if await wss.process_message(message, on_message):
                    return
            except ConnectionClosed:
                handler = await wss.open(restore=True)

    async def subscribe(self, wss: BitmexWssApi, subscr_channel, subscribe_name, symbol=None):
        assert await wss.subscribe(subscr_channel, subscribe_name, symbol)
        try:
            await asyncio.wait_for(
                self.consume(wss, wss.handler, self.on_message),
                timeout=5
            )
        except asyncio.TimeoutError:
            wss.logger.warning('No messages.')

    def validate_messages(self, subscr_name):
        for message in self.messages:
            header = message[subscr_name]
            assert Schema(fields.WS_MESSAGE_HEADER_FIELDS).validate(header) == header
            for data in header['d']:
                assert Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name]).validate(data) == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name, symbol', [
            ('tbitmex', 'order_book', BITMEX_SYMBOL),
            ('tbitmex', 'order_book', None),
            ('tbitmex', 'quote_bin', BITMEX_SYMBOL),
            ('tbitmex', 'quote_bin', None),
            ('tbitmex', 'symbol', BITMEX_SYMBOL),
            ('tbitmex', 'symbol', None),
            ('tbitmex', 'trade', BITMEX_SYMBOL),
            ('tbitmex', 'trade', None),
            ('tbitmex', 'wallet', None),
            ('tbitmex', 'order', BITMEX_SYMBOL),
            ('tbitmex', 'order', None),
            ('tbitmex', 'position', BITMEX_SYMBOL),
            ('tbitmex', 'position', None),
        ],
        indirect=['wss'],
    )
    async def test_subscription(self, wss: BitmexWssApi, subscr_name: str, symbol: Optional[str]):
        subscr_channel = '1'
        self.reset()
        if subscr_name in wss.auth_subscribers:
            await wss.authenticate()
        await self.subscribe(wss, subscr_channel, subscr_name, symbol)
        self.validate_messages(subscr_name)
        self.reset()
        assert wss._subscriptions == {subscr_name: {f"{symbol or '*'}".lower(): {subscr_channel}}}
        assert await wss.unsubscribe(subscr_channel, subscr_name, symbol)
        assert wss._subscriptions == {}
