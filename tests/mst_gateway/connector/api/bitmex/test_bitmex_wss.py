import json
import pytest
from copy import deepcopy
from typing import Optional
from schema import Schema
from mst_gateway.connector.api.stocks.bitmex.var import BITMEX_ORDER_STATUS_NEW, BITMEX_ORDER_DELETE_ACTION_STATUSES
from mst_gateway.storage import StateStorageKey
from tests.mst_gateway.connector import schema as fields
from mst_gateway.connector.api import OrderSchema
from mst_gateway.connector.api.stocks.bitmex import BitmexWssApi
import tests.config as cfg
from .data.storage import STORAGE_DATA
from .data import DEFAULT_TRADE_DATA, DEFAULT_QUOTE_BIN_DATA, DEFAULT_SYMBOL_DATA, DEFAULT_ORDER_BOOK_DATA, \
    DEFAULT_ORDER_DATA, DEFAULT_ORDER_SPLIT_DATA, DEFAULT_TRADE_SPLIT_DATA, DEFAULT_POSITION_DATA, DEFAULT_WALLET_DATA


def rest_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_TESTNET_AUTH_KEYS, [OrderSchema.margin1])
    }
    return name_map[name]


def wss_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_TESTNET_AUTH_KEYS, OrderSchema.margin1)
    }
    return name_map[name]


@pytest.fixture(params=['tbitmex'])
async def wss(request) -> BitmexWssApi:
    param = request.param
    test, auth, schema = wss_params(param)
    with BitmexWssApi(
            test=test,
            name=param,
            auth=auth,
            schema=schema,
            url='wss://ws.testnet.bitmex.com/realtime',
            state_storage=deepcopy(STORAGE_DATA)
    ) as wss:
        await wss.open()
        yield wss
        await wss.close()


class TestBitmexWssApi:
    @classmethod
    def init_partial_state(cls, wss: BitmexWssApi, subscr_name: str):
        exchange = wss.name
        schema = wss.schema
        wss.partial_state_data[subscr_name]['exchange_rates'] = deepcopy(
            STORAGE_DATA[StateStorageKey.exchange_rates][exchange][schema]
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss', ['tbitmex'],
        indirect=True,
    )
    async def test_authenticate(self, wss: BitmexWssApi):
        assert not wss.auth_connect
        await wss.authenticate()
        assert wss.auth_connect
        await wss.close()

    @pytest.mark.parametrize(
        'wss, subscr_name, subscriptions, expect', [
            (
                'tbitmex',
                'symbol',
                {"symbol": {cfg.BITMEX_SYMBOL.lower(): {"1"}, "*": {"1"}}},
                {"symbol": {"*": {"1"}}},
            ),
            (
                'tbitmex',
                'symbol',
                {"symbol": {cfg.BITMEX_SYMBOL.lower(): {"1"}, "*": {"2"}}},
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
            ('tbitmex', 'order', 'order', cfg.BITMEX_SYMBOL, (True, cfg.BITMEX_SYMBOL.lower())),
            ('tbitmex', None, '', cfg.BITMEX_SYMBOL, (True, cfg.BITMEX_SYMBOL.lower())),
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
            ('tbitmex', 'order', 'order', cfg.BITMEX_SYMBOL, True, True),
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
            ('tbitmex', 'order', 'order', cfg.BITMEX_SYMBOL, True, (True, cfg.BITMEX_SYMBOL.lower())),
            ('tbitmex', None, '', cfg.BITMEX_SYMBOL, True, (True, cfg.BITMEX_SYMBOL.lower())),
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
            ('tbitmex', 'order', 'order', cfg.BITMEX_SYMBOL, True, False),
            ('tbitmex', 'order', 'order', cfg.BITMEX_SYMBOL, False, True),
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
            ('tbitmex', 'trade', DEFAULT_TRADE_DATA[OrderSchema.margin1]),
            ('tbitmex', 'quote_bin', DEFAULT_QUOTE_BIN_DATA[OrderSchema.margin1]),
            ('tbitmex', 'symbol', DEFAULT_SYMBOL_DATA[OrderSchema.margin1]),
            ('tbitmex', 'order_book', DEFAULT_ORDER_BOOK_DATA[OrderSchema.margin1]),
            ('tbitmex', 'order', DEFAULT_ORDER_DATA[OrderSchema.margin1]),
            ('tbitmex', 'position', DEFAULT_POSITION_DATA[OrderSchema.margin1]),
        ],
        indirect=['wss']
    )
    async def test_get_data(self, wss: BitmexWssApi, subscr_name: str, default_data: dict):
        self.init_partial_state(wss, subscr_name)
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
        'wss, subscr_name, default_data', [
            ('tbitmex', 'trade', DEFAULT_TRADE_DATA[OrderSchema.margin1]),
            ('tbitmex', 'quote_bin', DEFAULT_QUOTE_BIN_DATA[OrderSchema.margin1]),
            ('tbitmex', 'symbol', DEFAULT_SYMBOL_DATA[OrderSchema.margin1]),
            ('tbitmex', 'order_book', DEFAULT_ORDER_BOOK_DATA[OrderSchema.margin1]),
            ('tbitmex', 'order', DEFAULT_ORDER_DATA[OrderSchema.margin1]),
            ('tbitmex', 'position', DEFAULT_POSITION_DATA[OrderSchema.margin1]),
        ],
        indirect=['wss']
    )
    async def test_get_state(self, wss: BitmexWssApi, subscr_name: str, default_data: dict):
        self.init_partial_state(wss, subscr_name)
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
            ('tbitmex', cfg.BITMEX_SYMBOL),
            ('tbitmex', None),
            ('tbitmex', 'NOOT_IN_STORAGE'),
        ],
        indirect=['wss']
    )
    def test_get_state_data(self, wss: BitmexWssApi, symbol: Optional[str]):
        state = wss.get_state_data(symbol)
        assert state == STORAGE_DATA[StateStorageKey.symbol][wss.name][wss.schema].get((symbol or '').lower())

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name, default_data', [
            ('tbitmex', 'wallet', DEFAULT_WALLET_DATA[OrderSchema.margin1])
        ],
        indirect=['wss']
    )
    async def test_get_wallet_data(self, wss: BitmexWssApi, subscr_name: str, default_data: dict):
        schema = wss.schema
        self.init_partial_state(wss, subscr_name)
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        data_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name][schema])
        summary_schema = Schema(fields.SUMMARY_FIELDS)
        balance_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS['balance'][schema])
        for data in default_data:
            message = json.loads(data['message'])
            wss_data = await wss.get_data(deepcopy(message))
            _data = wss_data[subscr_name]
            assert header_schema.validate(_data) == _data
            for d in _data['d']:
                assert data_schema.validate(d) == d
                for key in ('tbl', 'tupnl', 'tmbl'):
                    assert summary_schema.validate(d[key]) == d[key]
                for balance in d['bls']:
                    assert balance_schema.validate(balance) == balance
            assert _data == data['expect'][subscr_name]


    @pytest.mark.parametrize(
        'wss, default_data, expect', [
            ('tbitmex', DEFAULT_ORDER_DATA[OrderSchema.margin1], DEFAULT_ORDER_SPLIT_DATA[OrderSchema.margin1])
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
            ('tbitmex', DEFAULT_TRADE_DATA[OrderSchema.margin1], DEFAULT_TRADE_SPLIT_DATA[OrderSchema.margin1])
        ],
        indirect=['wss']
    )
    def test_split_trade(self, wss: BitmexWssApi, default_data: dict, expect: list):
        for i, data in enumerate(default_data):
            message = json.loads(data['message'])
            wss_data = wss.split_trade(deepcopy(message))
            assert wss_data == expect[i]

    @pytest.mark.parametrize(
        'wss, order_status, expect', [
            ('tbitmex', BITMEX_ORDER_STATUS_NEW, 'insert'),
            ('tbitmex', BITMEX_ORDER_DELETE_ACTION_STATUSES, 'delete'),
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
        from websockets.exceptions import ConnectionClosed
        while True:
            try:
                message = await handler.recv()
                if await wss.process_message(message, on_message):
                    break
            except ConnectionClosed:
                handler = await wss.open(restore=True)

    async def subscribe(self, wss: BitmexWssApi, subscr_channel, subscribe_name, symbol=None):
        assert await wss.subscribe(subscr_channel, subscribe_name, symbol)
        await self.consume(wss, wss.handler, self.on_message)

    def validate_messages(self, subscr_name, symbol=None):
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        data_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
        for message in self.messages:
            assert header_schema.validate(message[subscr_name]) == message[subscr_name]
            for data in message[subscr_name]['d']:
                assert data_schema.validate(data) == data
                if symbol:
                    assert data['s'].lower() == symbol.lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name', [
            ('tbitmex', 'order_book'),
            ('tbitmex', 'quote_bin'),
            ('tbitmex', 'symbol'),
            ('tbitmex', 'trade')
        ],
        indirect=['wss'],
    )
    async def test_subscription(self, wss: BitmexWssApi, subscr_name: str):
        subscr_channel = '1'
        symbol = cfg.BITMEX_SYMBOL
        self.reset()
        if subscr_name == 'quote_bin':
            await self.subscribe(wss, subscr_channel, subscr_name, symbol)
            self.validate_messages(subscr_name, symbol)
            self.reset()
            assert wss._subscriptions == {subscr_name: {symbol.lower(): {subscr_channel}}}
            assert await wss.unsubscribe(subscr_channel, subscr_name, symbol)
            assert wss._subscriptions == {}
        await self.subscribe(wss, subscr_channel, subscr_name)
        self.validate_messages(subscr_name)
        self.reset()
        assert wss._subscriptions == {subscr_name: {'*': {subscr_channel}}}
        assert await wss.unsubscribe(subscr_channel, subscr_name)
        assert wss._subscriptions == {}
