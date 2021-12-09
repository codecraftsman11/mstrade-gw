import json
import pytest
from copy import deepcopy
from mst_gateway.connector.api import schema as fields
from mst_gateway.storage.var import StateStorageKey
from mst_gateway.connector.api.stocks.binance import BinanceWssApi, BinanceFuturesWssApi, BinanceFuturesCoinWssApi
from mst_gateway.connector.api.stocks.binance.wss import subscribers
from mst_gateway.connector.api.types import OrderSchema
from mst_gateway.connector.api.utils import parse_message
from tests import config as cfg
from .data import storage as state_data
from .data import order as order_message
from .data import order_book as order_book_message
from .data import position as position_message
from .data import quote_bin as quote_message
from .data import symbol as symbol_message
from .data import trade as trade_message
from .data import wallet as wallet_message
from .test_binance_rest import get_symbol


def ws_class(name):
    name_map = {'tsbinance': BinanceWssApi,
                'tfbinance': BinanceFuturesWssApi,
                'tfcbinance': BinanceFuturesCoinWssApi}
    return name_map[name]


def wss_params(param):
    param_map = {
        'tsbinance': (OrderSchema.exchange, 'tbinance.tsbinance',
                      cfg.BINANCE_SPOT_TESTNET_WSS_API_URL, cfg.BINANCE_SPOT_TESTNET_AUTH_KEYS),
        'tfbinance': (OrderSchema.futures, 'tbinance.tfbinance',
                      cfg.BINANCE_FUTURES_TESTNET_WSS_API_URL, cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS),
        'tfcbinance': (OrderSchema.futures_coin, 'tbinance.tfbinance',
                       cfg.BINANCE_FUTURES_COIN_TESTNET_WSS_API_URL, cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS),
    }
    return param_map[param]


@pytest.fixture(params=['tsbinance', 'tfbinance', 'tfcbinance'])
async def wss(request) -> BinanceWssApi:
    param = request.param
    api_class = ws_class(param)
    schema, account_name, url, auth = wss_params(param)
    with api_class(test=True, schema=schema, name='tbinance', account_name=account_name, url=url, auth=auth,
                   state_storage=deepcopy(state_data.STORAGE_DATA)) as api:
        await api.open()
        yield api
        await api.close()


class TestBinanceWssApi:

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

    async def subscribe(self, wss, subscr_channel, subscr_name, symbol=None):
        assert await wss.subscribe(subscr_channel, subscr_name, symbol)
        await self.consume(wss, wss.handler, self.on_message)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    async def test__restore_subscriptions(self, wss: BinanceWssApi):
        symbol = get_symbol(wss.schema)
        subscriptions = {'symbol': {symbol.lower(): {'1'}}, 'order': {symbol.lower(): {'1'}}}
        wss._subscriptions = subscriptions
        await wss._restore_subscriptions()
        assert wss._subscriptions == subscriptions
        wss.auth_connect = False
        await wss._restore_subscriptions()
        assert wss._subscriptions == {'symbol': {symbol.lower(): {'1'}}}
        assert await wss.unsubscribe('1', 'symbol', symbol)
        assert await wss.unsubscribe('1', 'order', symbol)
        assert wss._subscriptions == {}

    @pytest.mark.asyncio
    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    async def test_open_auth(self, wss: BinanceWssApi):
        assert await wss.open(is_auth=True)

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_is_registered(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert not wss.is_registered(subscr_name)
        assert not wss.is_registered(subscr_name, symbol=symbol)
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1'}}}
        assert wss.is_registered(subscr_name)
        assert wss.is_registered(subscr_name, symbol=symbol)
        assert not wss.is_registered(subscr_name, symbol='NOT_REGISTERED')
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        assert wss.is_registered(subscr_name)
        assert wss.is_registered(subscr_name, symbol=symbol)
        assert wss.is_registered(subscr_name, symbol='NOT_REGISTERED')

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_is_unregistered(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert wss.is_unregistered(subscr_name)
        assert wss.is_unregistered(subscr_name, symbol)
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1'}}}
        assert wss.is_unregistered(subscr_name)
        assert not wss.is_unregistered(subscr_name, symbol)
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        assert not wss.is_unregistered(subscr_name)
        assert wss.is_unregistered(subscr_name, symbol)

    @pytest.mark.parametrize(
        'wss, subscriptions, expect', [
            ('tsbinance', {'symbol': {'btcusdt': {'1'}, '*': {'1'}}},
             {'symbol': {'*': {'1'}}}),
            ('tsbinance', {'symbol': {'btcusdt': {'1'}, '*': {'2'}}},
             {'symbol': {'*': {'1', '2'}}}),
            ('tfbinance', {'symbol': {'btcusdt': {'1'}, '*': {'1'}}},
             {'symbol': {'*': {'1'}}}),
            ('tfbinance', {'symbol': {'btcusdt': {'1'}, '*': {'2'}}},
             {'symbol': {'*': {'1', '2'}}}),
            ('tfcbinance', {'symbol': {'btcusd_perp': {'1'}, '*': {'1'}}},
             {'symbol': {'*': {'1'}}}),
            ('tfcbinance', {'symbol': {'btcusd_perp': {'1'}, '*': {'2'}}},
             {'symbol': {'*': {'1', '2'}}}),
        ],
        indirect=['wss'],
    )
    def test_remap_subscriptions(self, wss: BinanceWssApi, subscriptions, expect):
        wss._subscriptions = subscriptions
        assert wss.remap_subscriptions('symbol') is None
        assert wss._subscriptions == expect

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_register(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert wss.register('1', subscr_name, symbol) == (True, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1'}}}
        assert wss.register('2', subscr_name, symbol) == (True, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.register('1', subscr_name, 'ANY') == (True, 'any')
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}, 'any': {'1'}}}
        assert wss.register('3', subscr_name) == (True, '*')
        assert wss._subscriptions == {subscr_name: {'*': {'1', '2', '3'}}}
        assert wss.register('4', subscr_name, symbol) == (True, '*')
        assert wss._subscriptions == {subscr_name: {'*': {'1', '2', '3', '4'}}}

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_unregister(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert wss.unregister('1', subscr_name) == (False, None)
        assert wss._subscriptions == {}
        assert wss.unregister('1', subscr_name, 'NOT_REGISTERED') == (False, None)
        assert wss._subscriptions == {}
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name) == (False, '*')
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name, 'NOT_REGISTERED') == (False, 'not_registered')
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name, symbol) == (False, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1'}}}
        assert wss.unregister('3', subscr_name, symbol) == (False, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1'}}}
        assert wss.unregister('2', subscr_name, symbol) == (True, symbol.lower())
        assert wss._subscriptions == {}
        wss._subscriptions = {subscr_name: {'*': {'1', '2'}}}
        assert wss.unregister('1', subscr_name) == (False, '*')
        assert wss._subscriptions == {subscr_name: {'*': {'2'}}}
        assert wss.unregister('2', subscr_name, symbol) == (True, '*')
        assert wss._subscriptions == {}

    @pytest.mark.parametrize(
        'wss, name, expect', [('tsbinance', 'order', subscribers.BinanceOrderSubscriber),
                              ('tsbinance', 'order_book', subscribers.BinanceOrderBookSubscriber),
                              ('tsbinance', 'position', subscribers.BinanceQuoteBinSubscriber),
                              ('tsbinance', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
                              ('tsbinance', 'symbol', subscribers.BinanceSymbolSubscriber),
                              ('tsbinance', 'trade', subscribers.BinanceTradeSubscriber),
                              ('tsbinance', 'wallet', subscribers.BinanceWalletSubscriber),
                              ('tsbinance', 'not_exist', None),
                              ('tfbinance', 'order', subscribers.BinanceOrderSubscriber),
                              ('tfbinance', 'order_book', subscribers.BinanceOrderBookSubscriber),
                              ('tfbinance', 'position', subscribers.BinanceFuturesPositionSubscriber),
                              ('tfbinance', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
                              ('tfbinance', 'symbol', subscribers.BinanceFuturesSymbolSubscriber),
                              ('tfbinance', 'trade', subscribers.BinanceTradeSubscriber),
                              ('tfbinance', 'wallet', subscribers.BinanceWalletSubscriber),
                              ('tfbinance', 'not_exist', None),
                              ('tfcbinance', 'order', subscribers.BinanceOrderSubscriber),
                              ('tfcbinance', 'order_book', subscribers.BinanceOrderBookSubscriber),
                              ('tfcbinance', 'position', subscribers.BinanceFuturesCoinPositionSubscriber),
                              ('tfcbinance', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
                              ('tfcbinance', 'symbol', subscribers.BinanceFuturesSymbolSubscriber),
                              ('tfcbinance', 'trade', subscribers.BinanceTradeSubscriber),
                              ('tfcbinance', 'wallet', subscribers.BinanceWalletSubscriber),
                              ('tfcbinance', 'not_exist', None)],
        indirect=['wss']
    )
    def test__get_subscriber(self, wss: BinanceWssApi, name, expect):
        assert isinstance(wss._get_subscriber(name), expect)

    def validate_messages(self, subscr_name, symbol=None):
        for message in self.messages:
            assert fields.data_valid(message[subscr_name], fields.WS_MESSAGE_HEADER_FIELDS)
            for data in message[subscr_name]['d']:
                assert fields.data_valid(data, fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
                if symbol:
                    assert data['s'].lower() == symbol.lower()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name', [('tsbinance', 'order_book'), ('tsbinance', 'quote_bin'),
                             ('tsbinance', 'symbol'), ('tsbinance', 'trade'),
                             ('tfbinance', 'order_book'), ('tfbinance', 'quote_bin'),
                             ('tfbinance', 'symbol'), ('tfbinance', 'trade'),
                             ('tfcbinance', 'order_book'), ('tfcbinance', 'quote_bin'),
                             ('tfcbinance', 'symbol'), ('tfcbinance', 'trade')],
        indirect=['wss'],
    )
    async def test_subscription(self, wss: BinanceWssApi, subscr_name):
        subscr_channel = '1'
        self.reset()
        await self.subscribe(wss, subscr_channel, subscr_name)
        self.validate_messages(subscr_name)
        self.reset()
        assert wss._subscriptions == {subscr_name: {'*': {subscr_channel}}}
        assert await wss.unsubscribe(subscr_channel, subscr_name)
        assert wss._subscriptions == {}
        symbol = get_symbol(wss.schema)
        await self.subscribe(wss, subscr_channel, subscr_name, symbol)
        self.validate_messages(subscr_name, symbol)
        self.reset()
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {subscr_channel}}}
        assert await wss.unsubscribe(subscr_channel, subscr_name, symbol)
        assert wss._subscriptions == {}

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_get_state(self, wss: BinanceWssApi):
        assert wss.get_state('any', 'ANY') is None

    @pytest.mark.parametrize(
        'wss, symbol', [
            ('tsbinance', None), ('tsbinance', 'BTCUSDT'), ('tsbinance', 'NOT_IN_STORAGE'),
            ('tfbinance', None), ('tfbinance', 'BTCUSDT'), ('tfbinance', 'NOT_IN_STORAGE'),
            ('tfcbinance', None), ('tfcbinance', 'BTCUSD_PERP'), ('tfcbinance', 'NOT_IN_STORAGE')
        ],
        indirect=['wss'],
    )
    def test_get_state_data(self, wss: BinanceWssApi, symbol):
        assert wss.get_state_data(symbol) == state_data.STORAGE_DATA[
            StateStorageKey.symbol
        ][wss.name][wss.schema].get((symbol or '').lower())

    @pytest.mark.parametrize('wss', ['tsbinance', 'tfbinance', 'tfcbinance'], indirect=True)
    def test_parse_message(self, wss: BinanceWssApi):
        assert parse_message(json.dumps({'result': None, 'id': 1})) == {'result': None, 'id': 1}
        assert parse_message('{result: None, id: 1}') == {'raw': '{result: None, id: 1}'}
        assert parse_message({'result': None, 'id': 1}) is None

    @pytest.mark.parametrize(
        'wss, message, expect', [
            ('tsbinance', order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tsbinance', wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tfbinance', order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.futures],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.futures],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.futures],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.futures],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.futures],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfbinance', wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.futures],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tfcbinance', order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.futures_coin],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.futures_coin],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.futures_coin],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.futures_coin],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.futures_coin],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.futures_coin],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
        ],
        indirect=['wss'],
    )
    def test__lookup_table(self, wss: BinanceWssApi, message, expect):
        assert wss._lookup_table(message) == expect

    @pytest.mark.parametrize(
        'wss, status, expect', [
            ('tsbinance', 'NEW', 'insert'), ('tfbinance', 'NEW', 'insert'), ('tfcbinance', 'NEW', 'insert'),
            ('tsbinance', 'FILLED', 'delete'), ('tsbinance', 'CANCELED', 'delete'),
            ('tsbinance', 'EXPIRED', 'delete'), ('tsbinance', 'REJECTED', 'delete'),
            ('tfbinance', 'FILLED', 'delete'), ('tfbinance', 'CANCELED', 'delete'),
            ('tfbinance', 'EXPIRED', 'delete'), ('tfbinance', 'REJECTED', 'delete'),
            ('tfcbinance', 'FILLED', 'delete'), ('tfcbinance', 'CANCELED', 'delete'),
            ('tfcbinance', 'EXPIRED', 'delete'), ('tfcbinance', 'REJECTED', 'delete'),
            ('tsbinance', 'PARTIALLY_FILLED', 'update'), ('tsbinance', 'NEW_INSURANCE', 'update'),
            ('tsbinance', 'NEW_ADL', 'update'),
            ('tfbinance', 'PARTIALLY_FILLED', 'update'), ('tfbinance', 'NEW_INSURANCE', 'update'),
            ('tfbinance', 'NEW_ADL', 'update'),
            ('tfcbinance', 'PARTIALLY_FILLED', 'update'), ('tfcbinance', 'NEW_INSURANCE', 'update'),
            ('tfcbinance', 'NEW_ADL', 'update'),
        ],
        indirect=['wss'],
    )
    def test_define_action_by_order_status(self, wss: BinanceWssApi, status, expect):
        assert wss.define_action_by_order_status(status) == expect

    @pytest.mark.parametrize(
        'wss, message, expect', [
            ('tsbinance', order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tsbinance', wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tfbinance', order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfbinance', wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tfcbinance', order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tfcbinance', wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin])],
        indirect=['wss'],
    )
    def test__split_message(self, wss: BinanceWssApi, message, expect):
        assert wss._split_message(deepcopy(message)) == expect
    #
    # def test_split_wallet(self, wss: BinanceWssApi):
    #     assert (
    #         wss.split_wallet(deepcopy(WALLET_LOOKUP_TABLE_RESULT))
    #         is None
    #     )
    #     wss._subscriptions = {"wallet": {"btc": {"1"}}}
    #     assert (
    #         wss.split_wallet(deepcopy(WALLET_LOOKUP_TABLE_RESULT))
    #         == WALLET_SPLIT_MESSAGE_RESULTS[0]
    #     )
    #
    # @pytest.mark.parametrize(
    #     "messages, results",
    #     [
    #         (ORDER_BOOK_SPLIT_MESSAGE_RESULTS, ORDER_BOOK_GET_DATA_RESULTS),
    #         (ORDER_SPLIT_MESSAGE_RESULTS, ORDER_GET_DATA_RESULTS),
    #         (QUOTE_BIN_SPLIT_MESSAGE_RESULTS, QUOTE_BIN_GET_DATA_RESULTS),
    #         (TRADE_SPLIT_MESSAGE_RESULTS, TRADE_GET_DATA_RESULTS),
    #         (WALLET_SPLIT_MESSAGE_RESULTS, WALLET_GET_DATA_RESULTS),
    #     ],
    # )
    # def test_get_data(
    #     self, wss: BinanceWssApi, messages, results
    # ):
    #     for i, message in enumerate(messages):
    #         assert wss.get_data(message) == results[i]
    #
    # @pytest.mark.parametrize(
    #     "messages, results",
    #     [
    #         (
    #             SYMBOL_DETAIL_SPLIT_MESSAGE_RESULTS,
    #             SYMBOL_DETAIL_GET_DATA_RESULTS,
    #         ),
    #         (SYMBOL_SPLIT_MESSAGE_RESULTS, SYMBOL_GET_DATA_RESULTS),
    #     ],
    # )
    # def test_get_data_symbol(
    #     self, wss: BinanceWssApi, messages, results
    # ):
    #     for i, message in enumerate(messages):
    #         response = wss.get_data(message)
    #         for j, data in enumerate(response["symbol"]["data"]):
    #             data["created"] = results[i]["symbol"]["data"][j]["created"]
    #         assert response == results[i]
    #
    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     "message, results",
    #     [
    #         (ORDER_MESSAGE, ORDER_GET_DATA_RESULTS),
    #         (ORDER_BOOK_MESSAGE, ORDER_BOOK_GET_DATA_RESULTS),
    #         (QUOTE_BIN_MESSAGE, QUOTE_BIN_GET_DATA_RESULTS),
    #         (TRADE_MESSAGE, TRADE_GET_DATA_RESULTS),
    #     ],
    # )
    # async def test_process_message(
    #     self, wss: BinanceWssApi, message, results
    # ):
    #     self.reset()
    #     assert not self.data
    #     await wss.process_message(
    #         json.dumps(deepcopy(message)), self.on_message
    #     )
    #     assert self.data
    #     assert self.data == results
    #     self.reset()
    #
    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     "message, results",
    #     [
    #         (SYMBOL_DETAIL_MESSAGE, SYMBOL_DETAIL_GET_DATA_RESULTS),
    #         (SYMBOL_MESSAGE, SYMBOL_GET_DATA_RESULTS),
    #     ],
    # )
    # async def test_process_symbol_message(
    #     self, wss: BinanceWssApi, message, results
    # ):
    #     self.reset()
    #     assert not self.data
    #     await wss.process_message(
    #         json.dumps(deepcopy(message)), self.on_message
    #     )
    #     assert self.data
    #     for i, message in enumerate(results):
    #         for j, obj in enumerate(message["symbol"]["data"]):
    #             self.data[i]["symbol"]["data"][j]["created"] = obj["created"]
    #     assert self.data == results
    #     self.reset()
    #
    # @pytest.mark.asyncio
    # async def test_process_wallet_message(
    #     self, wss: BinanceWssApi
    # ):
    #     self.reset()
    #     assert not self.data
    #     wss._subscriptions = {"wallet": {"*": {"1"}}}
    #     await wss.process_message(
    #         json.dumps(deepcopy(WALLET_MESSAGE)), self.on_message
    #     )
    #     assert self.data == PROCESS_WALLET_MESSAGE_RESULT
    #     self.reset()
