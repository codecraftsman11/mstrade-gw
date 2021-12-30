import asyncio
import logging
import json
import pytest
from copy import deepcopy
from schema import Schema
from typing import Optional
from websockets.exceptions import ConnectionClosed
from mst_gateway.logging import init_logger
from mst_gateway.storage.var import StateStorageKey
from mst_gateway.connector.api.stocks.binance import BinanceWssApi, BinanceFuturesWssApi, BinanceFuturesCoinWssApi
from mst_gateway.connector.api.stocks.binance.wss import subscribers
from mst_gateway.connector.api.types import OrderSchema
from mst_gateway.connector.api.utils import parse_message
from tests.mst_gateway.connector import schema as fields
from tests import config as cfg
from .data import storage as state_data
from .data import order as order_message
from .data import order_book as order_book_message
from .data import position as position_message
from .data import quote_bin as quote_message
from .data import symbol as symbol_message
from .data import trade as trade_message
from .data import wallet as wallet_message
from .test_binance_rest import get_symbol, get_asset, get_liquidation_kwargs


def ws_class(name):
    name_map = {'tbinance_spot': BinanceWssApi, 'tbinance_futures': BinanceFuturesWssApi,
                'tbinance_futures_coin': BinanceFuturesCoinWssApi}
    return name_map[name]


def wss_params(param):
    param_map = {
        'tbinance_spot': (OrderSchema.exchange, 'tbinance.tbinance_spot.1',
                          cfg.BINANCE_SPOT_TESTNET_WSS_API_URL,
                          cfg.BINANCE_SPOT_TESTNET_AUTH_KEYS),
        'tbinance_futures': (OrderSchema.futures, 'tbinance.tbinance_futures.2',
                             cfg.BINANCE_FUTURES_TESTNET_WSS_API_URL,
                             cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS),
        'tbinance_futures_coin': (OrderSchema.futures_coin, 'tbinance.tbinance_futures.2',
                                  cfg.BINANCE_FUTURES_COIN_TESTNET_WSS_API_URL,
                                  cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS),
    }
    return param_map[param]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


@pytest.fixture(params=['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'])
async def wss(request, _debug) -> BinanceWssApi:
    param = request.param
    api_class = ws_class(param)
    schema, account_name, url, auth = wss_params(param)
    with api_class(test=True, schema=schema, name='tbinance', account_name=account_name, url=url, auth=auth,
                   state_storage=deepcopy(state_data.STORAGE_DATA),
                   logger=_debug['logger']) as api:
        await api.open()
        yield api
        await api.close()


@pytest.fixture(params=['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'])
async def wss_auth(request, _debug) -> BinanceWssApi:
    param = request.param
    api_class = ws_class(param)
    schema, account_name, url, auth = wss_params(param)
    with api_class(test=True, schema=schema, name='tbinance', account_name=account_name, url=url, auth=auth,
                   state_storage=deepcopy(state_data.STORAGE_DATA),
                   logger=_debug['logger']) as api:
        await api.open(is_auth=True)
        yield api
        await api.close()


def get_position_partial_state_data(schema):
    leverage_brackets, position_state = get_liquidation_kwargs(schema)
    if schema in (OrderSchema.futures, OrderSchema.futures_coin):
        symbol = get_symbol(schema)
        position_state[symbol.lower()].update({'volume': 0, 'side': None})
    return leverage_brackets, position_state


class TestBinanceWssApi:

    @pytest.mark.asyncio
    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
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
    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
    async def test_open_auth(self, wss: BinanceWssApi):
        assert await wss.open(is_auth=True)

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
    def test_is_registered(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert not wss.is_registered(subscr_name)
        assert not wss.is_registered(subscr_name, symbol=symbol)
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1'}}}
        assert not wss.is_registered(subscr_name)
        assert wss.is_registered(subscr_name, symbol=symbol)
        assert not wss.is_registered(subscr_name, symbol='NOT_REGISTERED')
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        assert wss.is_registered(subscr_name)
        assert wss.is_registered(subscr_name, symbol=symbol)
        assert wss.is_registered(subscr_name, symbol='NOT_REGISTERED')

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
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
        'wss, subscriptions, expect', [('tbinance_spot', {'symbol': {'btcusdt': {'1'}, '*': {'1'}}},
                                       {'symbol': {'*': {'1'}}}),
                                       ('tbinance_spot', {'symbol': {'btcusdt': {'1'}, '*': {'2'}}},
                                       {'symbol': {'*': {'1', '2'}}}),
                                       ('tbinance_futures', {'symbol': {'btcusdt': {'1'}, '*': {'1'}}},
                                       {'symbol': {'*': {'1'}}}),
                                       ('tbinance_futures', {'symbol': {'btcusdt': {'1'}, '*': {'2'}}},
                                       {'symbol': {'*': {'1', '2'}}}),
                                       ('tbinance_futures_coin', {'symbol': {'btcusd_perp': {'1'}, '*': {'1'}}},
                                       {'symbol': {'*': {'1'}}}),
                                       ('tbinance_futures_coin', {'symbol': {'btcusd_perp': {'1'}, '*': {'2'}}},
                                       {'symbol': {'*': {'1', '2'}}})],
        indirect=['wss'],
    )
    def test_remap_subscriptions(self, wss: BinanceWssApi, subscriptions, expect):
        wss._subscriptions = subscriptions
        assert wss.remap_subscriptions('symbol') is None
        assert wss._subscriptions == expect

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
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

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
    def test_unregister(self, wss: BinanceWssApi):
        subscr_name = 'symbol'
        symbol = get_symbol(wss.schema)
        assert wss.unregister('1', subscr_name) == (False, None)
        assert wss._subscriptions == {}
        assert wss.unregister('1', subscr_name, 'NOT_REGISTERED') == (False, 'NOT_REGISTERED')
        assert wss._subscriptions == {}
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name) == (False, '*')
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name, 'NOT_REGISTERED') == (False, 'not_registered')
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'1', '2'}}}
        assert wss.unregister('1', subscr_name, symbol) == (False, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'2'}}}
        assert wss.unregister('3', subscr_name, symbol) == (False, symbol.lower())
        assert wss._subscriptions == {subscr_name: {symbol.lower(): {'2'}}}
        assert wss.unregister('2', subscr_name, symbol) == (True, symbol.lower())
        assert wss._subscriptions == {}
        wss._subscriptions = {subscr_name: {'*': {'1', '2'}}}
        assert wss.unregister('1', subscr_name) == (False, '*')
        assert wss._subscriptions == {subscr_name: {'*': {'2'}}}
        assert wss.unregister('2', subscr_name, symbol) == (True, '*')
        assert wss._subscriptions == {}

    @pytest.mark.parametrize(
        'wss, subscr_name, expect', [
            ('tbinance_spot', 'order', subscribers.BinanceOrderSubscriber),
            ('tbinance_spot', 'order_book', subscribers.BinanceOrderBookSubscriber),
            ('tbinance_spot', 'position', subscribers.BinancePositionSubscriber),
            ('tbinance_spot', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
            ('tbinance_spot', 'symbol', subscribers.BinanceSymbolSubscriber),
            ('tbinance_spot', 'trade', subscribers.BinanceTradeSubscriber),
            ('tbinance_spot', 'wallet', subscribers.BinanceWalletSubscriber),
            ('tbinance_futures', 'order', subscribers.BinanceOrderSubscriber),
            ('tbinance_futures', 'order_book', subscribers.BinanceOrderBookSubscriber),
            ('tbinance_futures', 'position', subscribers.BinanceFuturesPositionSubscriber),
            ('tbinance_futures', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
            ('tbinance_futures', 'symbol', subscribers.BinanceFuturesSymbolSubscriber),
            ('tbinance_futures', 'trade', subscribers.BinanceTradeSubscriber),
            ('tbinance_futures', 'wallet', subscribers.BinanceWalletSubscriber),
            ('tbinance_futures_coin', 'order', subscribers.BinanceOrderSubscriber),
            ('tbinance_futures_coin', 'order_book', subscribers.BinanceOrderBookSubscriber),
            ('tbinance_futures_coin', 'position', subscribers.BinanceFuturesCoinPositionSubscriber),
            ('tbinance_futures_coin', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
            ('tbinance_futures_coin', 'symbol', subscribers.BinanceFuturesSymbolSubscriber),
            ('tbinance_futures_coin', 'trade', subscribers.BinanceTradeSubscriber),
            ('tbinance_futures_coin', 'wallet', subscribers.BinanceWalletSubscriber),
        ],
        indirect=['wss']
    )
    def test__get_subscriber(self, wss: BinanceWssApi, subscr_name, expect):
        subscriber = wss._get_subscriber(subscr_name)
        assert isinstance(subscriber, expect)
        assert subscriber.subscription == subscr_name

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
    def test_get_state(self, wss: BinanceWssApi):
        assert wss.get_state('any', 'ANY') is None

    @pytest.mark.parametrize(
        'wss, symbol', [('tbinance_spot', None), ('tbinance_spot', 'BTCUSDT'),
                        ('tbinance_spot', 'NOT_IN_STORAGE'),
                        ('tbinance_futures', None), ('tbinance_futures', 'BTCUSDT'),
                        ('tbinance_futures', 'NOT_IN_STORAGE'),
                        ('tbinance_futures_coin', None), ('tbinance_futures_coin', 'BTCUSD_PERP'),
                        ('tbinance_futures_coin', 'NOT_IN_STORAGE')],
        indirect=['wss'],
    )
    def test_get_state_data(self, wss: BinanceWssApi, symbol):
        assert wss.get_state_data(symbol) == state_data.STORAGE_DATA[
            StateStorageKey.symbol
        ][wss.name][wss.schema].get((symbol or '').lower())

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_futures', 'tbinance_futures_coin'], indirect=True)
    def test_parse_message(self, wss: BinanceWssApi):
        assert parse_message(json.dumps({'result': None, 'id': 1})) == {'result': None, 'id': 1}
        assert parse_message('{result: None, id: 1}') == {'raw': '{result: None, id: 1}'}
        assert parse_message({'result': None, 'id': 1}) is None

    @pytest.mark.parametrize(
        'wss, subscr_name, message, expect', [
            ('tbinance_spot', 'order',
             order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'position',
             position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.exchange],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'trade',
             trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'wallet',
             wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.exchange]),
            ('tbinance_futures', 'order',
             order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.futures],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.futures],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'position',
             position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.futures],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.futures],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'trade',
             trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.futures],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'wallet',
             wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.futures],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures]),
            ('tbinance_futures_coin', 'order',
             order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.futures_coin],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.futures_coin],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'position',
             position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.futures_coin],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.futures_coin],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'trade',
             trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.futures_coin],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'wallet',
             wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.futures_coin],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin]),
        ],
        indirect=['wss'],
    )
    def test__lookup_table(self, wss: BinanceWssApi, subscr_name, message, expect):
        assert wss._lookup_table(message) == expect

    @pytest.mark.parametrize(
        'wss, status, expect', [('tbinance_spot', 'NEW', 'insert'),
                                ('tbinance_futures', 'NEW', 'insert'),
                                ('tbinance_futures_coin', 'NEW', 'insert'),
                                ('tbinance_spot', 'FILLED', 'delete'),
                                ('tbinance_spot', 'CANCELED', 'delete'),
                                ('tbinance_spot', 'EXPIRED', 'delete'),
                                ('tbinance_spot', 'REJECTED', 'delete'),
                                ('tbinance_futures', 'FILLED', 'delete'),
                                ('tbinance_futures', 'CANCELED', 'delete'),
                                ('tbinance_futures', 'EXPIRED', 'delete'),
                                ('tbinance_futures', 'REJECTED', 'delete'),
                                ('tbinance_futures_coin', 'FILLED', 'delete'),
                                ('tbinance_futures_coin', 'CANCELED', 'delete'),
                                ('tbinance_futures_coin', 'EXPIRED', 'delete'),
                                ('tbinance_futures_coin', 'REJECTED', 'delete'),
                                ('tbinance_spot', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_spot', 'NEW_INSURANCE', 'update'),
                                ('tbinance_spot', 'NEW_ADL', 'update'),
                                ('tbinance_futures', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_futures', 'NEW_INSURANCE', 'update'),
                                ('tbinance_futures', 'NEW_ADL', 'update'),
                                ('tbinance_futures_coin', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_futures_coin', 'NEW_INSURANCE', 'update'),
                                ('tbinance_futures_coin', 'NEW_ADL', 'update')],
        indirect=['wss'],
    )
    def test_define_action_by_order_status(self, wss: BinanceWssApi, status, expect):
        assert wss.define_action_by_order_status(status) == expect

    @pytest.mark.parametrize(
        'wss, subscr_name, message, expect', [
            ('tbinance_spot', 'order',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'position',
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'order',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'trade',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'wallet',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_futures', 'order',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'position',
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'trade',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'wallet',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'order',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures]),
            ('tbinance_futures_coin', 'order',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'position',
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'trade',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'wallet',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.futures_coin],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin]),
        ],
        indirect=['wss'],
    )
    def test__split_message(self, wss: BinanceWssApi, subscr_name, message, expect):
        if subscr_name == 'wallet' and wss.schema == OrderSchema.exchange:
            assert wss._split_message(deepcopy(message)) == [None]
            wss._subscriptions = {subscr_name: {'*': {'1'}}}
        assert wss._split_message(deepcopy(message)) == expect
        if subscr_name == 'wallet' and wss.schema == OrderSchema.exchange:
            wss._subscriptions = {subscr_name: {'btc': {'1'}}}
            _expect = deepcopy(expect)
            _expect[0]['data'][0]['B'].pop(1)
            assert wss._split_message(deepcopy(message)) == _expect

    @classmethod
    def validate_balances(cls, schema, balances):
        balance_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS['balance'][schema])
        for balance in balances:
            assert balance_schema.validate(balance) == balance

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, messages, expect', [('tbinance_spot',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
                                   wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.exchange]),
                                  ('tbinance_futures',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
                                   wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.futures]),
                                  ('tbinance_futures_coin',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
                                   wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.futures_coin])],
        indirect=['wss'],
    )
    async def test_get_wallet_data(self, wss: BinanceWssApi, messages, expect):
        subscr_name = 'wallet'
        schema = wss.schema
        self.init_partial_state(wss, subscr_name)
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        data_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name][schema])
        summary_schema = Schema(fields.SUMMARY_FIELDS)
        for i, message in enumerate(messages):
            assert await wss.get_data(deepcopy(message)) == {}

        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            _data = data[subscr_name]
            assert header_schema.validate(_data) == _data
            for d in _data['d']:
                assert data_schema.validate(d) == d
                assert summary_schema.validate(d['tbl']) == d['tbl']
                if schema in (OrderSchema.futures, OrderSchema.futures_coin):
                    for key in ('tupnl', 'tmbl', 'tbor', 'tist'):
                        assert summary_schema.validate(d[key]) == d[key]
                self.validate_balances(schema, d['bls'])
            assert data == expect[i]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, messages, expect', [('tbinance_spot',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
                                   wallet_message.DEFAULT_WALLET_DETAIL_GET_DATA_RESULT[OrderSchema.exchange]),
                                  ('tbinance_futures',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
                                   wallet_message.DEFAULT_WALLET_DETAIL_GET_DATA_RESULT[OrderSchema.futures]),
                                  ('tbinance_futures_coin',
                                   wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
                                   wallet_message.DEFAULT_WALLET_DETAIL_GET_DATA_RESULT[OrderSchema.futures_coin])],
        indirect=['wss'],
    )
    async def test_get_wallet_detail_data(self, wss: BinanceWssApi, messages, expect):
        subscr_name = 'wallet'
        schema = wss.schema
        self.init_partial_state(wss, subscr_name)
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)

        wss._subscriptions = {subscr_name: {get_asset(schema).lower(): {'1'}}}
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            _data = data.get(subscr_name)
            assert header_schema.validate(_data) == _data
            for d in _data['d']:
                self.validate_balances(schema, d['bls'])
            assert data == expect[i]

    @classmethod
    def init_partial_state(cls, wss: BinanceWssApi, subscr_name):
        exchange = wss.name
        schema = wss.schema
        symbol = get_symbol(schema)
        wss.partial_state_data[subscr_name]['exchange_rates'] = deepcopy(
            state_data.STORAGE_DATA[StateStorageKey.exchange_rates][exchange][schema]
        )
        if subscr_name == 'position':
            leverage_brackets, position_state = get_position_partial_state_data(schema)
            if schema == OrderSchema.exchange:
                position_state = {symbol.lower(): deepcopy(state_data.STORAGE_DATA[
                    f"{subscr_name}.{wss.account_id}.{exchange}.{OrderSchema.exchange}.{symbol}".lower()
                ])}
            wss.partial_state_data[subscr_name].update({
                'position_state': position_state,
                'leverage_brackets': {symbol.lower(): leverage_brackets},
            })

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, messages, expect', [('tbinance_spot',
                                   position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
                                   position_message.DEFAULT_POSITION_GET_DATA_RESULT[OrderSchema.exchange]),
                                  ('tbinance_futures',
                                   position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
                                   position_message.DEFAULT_POSITION_GET_DATA_RESULT[OrderSchema.futures]),
                                  ('tbinance_futures_coin',
                                   position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
                                   position_message.DEFAULT_POSITION_GET_DATA_RESULT[OrderSchema.futures_coin])],
        indirect=['wss'],
    )
    async def test_get_position_data(self, wss: BinanceWssApi, messages, expect):
        subscr_name = 'position'
        self.init_partial_state(wss, subscr_name)
        for i, message in enumerate(messages):
            assert await wss.get_data(deepcopy(message)) == {}

        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            self.validate_data(data, subscr_name)
            assert data == expect[i]

        self.init_partial_state(wss, subscr_name)
        schema = wss.schema
        symbol = get_symbol(schema)
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1'}}}
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            for i, message in enumerate(position_message.DEFAULT_POSITION_DETAIL_MESSAGES[schema]):
                data = await wss.get_data(deepcopy(message))
                self.validate_data(data, subscr_name)
                assert data == position_message.DEFAULT_POSITION_DETAIL_GET_DATA_RESULT[schema][i]

    @classmethod
    def validate_data(cls, data, subscr_name):
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        data_schema = Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name])
        _data = data[subscr_name]
        assert header_schema.validate(_data) == _data
        for d in _data['d']:
            assert data_schema.validate(d) == d

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss, subscr_name, messages, expect', [
            ('tbinance_spot', 'order',
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'symbol',
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_spot', 'trade',
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_futures', 'order',
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             order_message.DEFAULT_ORDER_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             order_book_message.DEFAULT_ORDER_BOOK_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             quote_message.DEFAULT_QUOTE_BIN_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'symbol',
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             symbol_message.DEFAULT_SYMBOL_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures', 'trade',
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures],
             trade_message.DEFAULT_TRADE_GET_DATA_RESULT[OrderSchema.futures]),
            ('tbinance_futures_coin', 'order',
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             order_message.DEFAULT_ORDER_GET_DATA_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             order_book_message.DEFAULT_ORDER_BOOK_GET_DATA_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             quote_message.DEFAULT_QUOTE_BIN_GET_DATA_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             symbol_message.DEFAULT_SYMBOL_GET_DATA_RESULT[OrderSchema.futures_coin]),
            ('tbinance_futures_coin', 'trade',
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.futures_coin],
             trade_message.DEFAULT_TRADE_GET_DATA_RESULT[OrderSchema.futures_coin]),
        ],
        indirect=['wss'],
    )
    async def test_get_data(self, wss: BinanceWssApi, subscr_name, messages, expect):
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            assert data.get(subscr_name, {}) == {}

        wss._subscriptions = {subscr_name: {'*': {'1'}}}
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            self.validate_data(data, subscr_name)
            assert data == expect[i]

        symbol = get_symbol(wss.schema)
        wss._subscriptions = {subscr_name: {symbol.lower(): {'1'}}}
        for i, message in enumerate(messages):
            data = await wss.get_data(deepcopy(message))
            self.validate_data(data, subscr_name)
            assert data == expect[i]


class TestSubscriptionBinanceWssApi:

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

    async def subscribe(self, wss, subscr_channel, subscr_name, symbol=None):
        assert await wss.subscribe(subscr_channel, subscr_name, symbol)
        try:
            await asyncio.wait_for(
                self.consume(wss, wss.handler, self.on_message),
                timeout=5
            )
        except asyncio.TimeoutError:
            wss.logger.warning('No messages.')

    def validate_messages(self, subscr_name, schema):
        header_schema = Schema(fields.WS_MESSAGE_HEADER_FIELDS)
        if subscr_name == 'wallet':
            subscr_schema = fields.WS_MESSAGE_DATA_FIELDS[subscr_name][schema]
        else:
            subscr_schema = fields.WS_MESSAGE_DATA_FIELDS[subscr_name]
        data_schema = Schema(subscr_schema)
        for message in self.messages:
            assert header_schema.validate(message[subscr_name]) == message[subscr_name]
            for data in message[subscr_name]['d']:
                assert data_schema.validate(data) == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss_auth, subscr_name, symbol', [
            ('tbinance_spot', 'order_book', 'BTCUSDT'), ('tbinance_spot', 'order_book', None),
            ('tbinance_spot', 'quote_bin', 'BTCUSDT'), ('tbinance_spot', 'quote_bin', None),
            ('tbinance_spot', 'symbol', 'BTCUSDT'), ('tbinance_spot', 'symbol', None),
            ('tbinance_spot', 'trade', 'BTCUSDT'), ('tbinance_spot', 'trade', None),
            ('tbinance_spot', 'wallet', None),
            ('tbinance_spot', 'order', 'BTCUSDT'), ('tbinance_spot', 'order', None),
            ('tbinance_spot', 'position', 'BTCUSDT'), ('tbinance_spot', 'position', None),
            ('tbinance_futures', 'order_book', 'BTCUSDT'), ('tbinance_futures', 'order_book', None),
            ('tbinance_futures', 'quote_bin', 'BTCUSDT'), ('tbinance_futures', 'quote_bin', None),
            ('tbinance_futures', 'symbol', 'BTCUSDT'), ('tbinance_futures', 'symbol', None),
            ('tbinance_futures', 'trade', 'BTCUSDT'), ('tbinance_futures', 'trade', None),
            ('tbinance_futures', 'wallet', None),
            ('tbinance_futures', 'order', 'BTCUSDT'), ('tbinance_futures', 'order', None),
            ('tbinance_futures', 'position', 'BTCUSDT'), ('tbinance_futures', 'position', None),
            ('tbinance_futures_coin', 'order_book', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'order_book', None),
            ('tbinance_futures_coin', 'quote_bin', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'quote_bin', None),
            ('tbinance_futures_coin', 'symbol', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'symbol', None),
            ('tbinance_futures_coin', 'trade', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'trade', None),
            ('tbinance_futures_coin', 'wallet', None),
            ('tbinance_futures_coin', 'order', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'order', None),
            ('tbinance_futures_coin', 'position', 'BTCUSD_PERP'), ('tbinance_futures_coin', 'position', None)
        ], indirect=['wss_auth'],
    )
    async def test_subscription(self, wss_auth: BinanceWssApi, subscr_name, symbol: Optional[str]):
        subscr_channel = '1'
        self.reset()
        if subscr_name == 'wallet':
            symbol = None
        await self.subscribe(wss_auth, subscr_channel, subscr_name, symbol)
        self.validate_messages(subscr_name, wss_auth.schema)
        self.reset()
        assert wss_auth._subscriptions == {subscr_name: {f"{symbol or '*'}".lower(): {subscr_channel}}}
        assert await wss_auth.unsubscribe(subscr_channel, subscr_name, symbol)
        assert wss_auth._subscriptions == {}
