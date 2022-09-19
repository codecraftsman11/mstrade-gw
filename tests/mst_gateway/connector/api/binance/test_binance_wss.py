import asyncio
import logging
import json
import pytest
from copy import deepcopy
from schema import Schema
from typing import Optional
from websockets.exceptions import ConnectionClosed

from mst_gateway.connector.api import PositionSide
from mst_gateway.logging import init_logger
from mst_gateway.storage.var import StateStorageKey
from mst_gateway.connector.api.stocks.binance import BinanceWssApi, BinanceMarginWssApi, BinanceMarginCoinWssApi
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
from .test_binance_rest import get_symbol, get_liquidation_kwargs


def ws_class(name):
    name_map = {'tbinance_spot': BinanceWssApi, 'tbinance_margin': BinanceMarginWssApi,
                'tbinance_margin_coin': BinanceMarginCoinWssApi}
    return name_map[name]


def wss_params(param):
    param_map = {
        'tbinance_spot': (OrderSchema.exchange, 'tbinance.tbinance_spot.1',
                          cfg.BINANCE_SPOT_TESTNET_WSS_API_URL,
                          cfg.BINANCE_SPOT_TESTNET_AUTH_KEYS),
        'tbinance_margin': (OrderSchema.margin, 'tbinance.tbinance_margin.2',
                            cfg.BINANCE_MARGIN_TESTNET_WSS_API_URL,
                            cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS),
        'tbinance_margin_coin': (OrderSchema.margin_coin, 'tbinance.tbinance_margin.2',
                                 cfg.BINANCE_FUTURES_COIN_TESTNET_WSS_API_URL,
                                 cfg.BINANCE_FUTURES_COIN_TESTNET_AUTH_KEYS),
    }
    return param_map[param]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


@pytest.fixture(params=['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'])
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


@pytest.fixture(params=['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'])
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
    if schema in (OrderSchema.margin, OrderSchema.margin_coin):
        symbol = get_symbol(schema)
        position_state[symbol.lower()][PositionSide.both].update({'volume': 0, 'side': None})
    return leverage_brackets, position_state


class TestBinanceWssApi:

    @pytest.mark.asyncio
    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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
    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
    async def test_open_auth(self, wss: BinanceWssApi):
        assert await wss.open(is_auth=True)

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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
                                       ('tbinance_margin', {'symbol': {'btcusdt': {'1'}, '*': {'1'}}},
                                       {'symbol': {'*': {'1'}}}),
                                       ('tbinance_margin', {'symbol': {'btcusdt': {'1'}, '*': {'2'}}},
                                       {'symbol': {'*': {'1', '2'}}}),
                                       ('tbinance_margin_coin', {'symbol': {'btcusd_perp': {'1'}, '*': {'1'}}},
                                       {'symbol': {'*': {'1'}}}),
                                       ('tbinance_margin_coin', {'symbol': {'btcusd_perp': {'1'}, '*': {'2'}}},
                                       {'symbol': {'*': {'1', '2'}}})],
        indirect=['wss'],
    )
    def test_remap_subscriptions(self, wss: BinanceWssApi, subscriptions, expect):
        wss._subscriptions = subscriptions
        assert wss.remap_subscriptions('symbol') is None
        assert wss._subscriptions == expect

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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
            ('tbinance_margin', 'order', subscribers.BinanceOrderSubscriber),
            ('tbinance_margin', 'order_book', subscribers.BinanceOrderBookSubscriber),
            ('tbinance_margin', 'position', subscribers.BinanceMarginPositionSubscriber),
            ('tbinance_margin', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
            ('tbinance_margin', 'symbol', subscribers.BinanceMarginSymbolSubscriber),
            ('tbinance_margin', 'trade', subscribers.BinanceTradeSubscriber),
            ('tbinance_margin', 'wallet', subscribers.BinanceWalletSubscriber),
            ('tbinance_margin_coin', 'order', subscribers.BinanceOrderSubscriber),
            ('tbinance_margin_coin', 'order_book', subscribers.BinanceOrderBookSubscriber),
            ('tbinance_margin_coin', 'position', subscribers.BinanceMarginCoinPositionSubscriber),
            ('tbinance_margin_coin', 'quote_bin', subscribers.BinanceQuoteBinSubscriber),
            ('tbinance_margin_coin', 'symbol', subscribers.BinanceMarginSymbolSubscriber),
            ('tbinance_margin_coin', 'trade', subscribers.BinanceTradeSubscriber),
            ('tbinance_margin_coin', 'wallet', subscribers.BinanceWalletSubscriber),
        ],
        indirect=['wss']
    )
    def test__get_subscriber(self, wss: BinanceWssApi, subscr_name, expect):
        subscriber = wss._get_subscriber(subscr_name)
        assert isinstance(subscriber, expect)
        assert subscriber.subscription == subscr_name

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
    def test_get_state(self, wss: BinanceWssApi):
        assert wss.get_state('any', 'ANY') is None

    @pytest.mark.parametrize(
        'wss, symbol', [('tbinance_spot', None), ('tbinance_spot', 'BTCUSDT'),
                        ('tbinance_spot', 'NOT_IN_STORAGE'),
                        ('tbinance_margin', None), ('tbinance_margin', 'BTCUSDT'),
                        ('tbinance_margin', 'NOT_IN_STORAGE'),
                        ('tbinance_margin_coin', None), ('tbinance_margin_coin', 'BTCUSD_PERP'),
                        ('tbinance_margin_coin', 'NOT_IN_STORAGE')],
        indirect=['wss'],
    )
    def test_get_state_data(self, wss: BinanceWssApi, symbol):
        assert wss.get_state_data(symbol) == state_data.STORAGE_DATA[
            f"{StateStorageKey.symbol}.{wss.name}.{wss.schema}"].get((symbol or '').lower())

    @pytest.mark.parametrize('wss', ['tbinance_spot', 'tbinance_margin', 'tbinance_margin_coin'], indirect=True)
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
            ('tbinance_margin', 'order',
             order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.margin],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.margin],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'position',
             position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.margin],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.margin],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'trade',
             trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.margin],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'wallet',
             wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.margin],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.margin]),
            ('tbinance_margin_coin', 'order',
             order_message.DEFAULT_ORDER_MESSAGE[OrderSchema.margin_coin],
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_MESSAGE[OrderSchema.margin_coin],
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'position',
             position_message.DEFAULT_POSITION_MESSAGE[OrderSchema.margin_coin],
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_MESSAGE[OrderSchema.margin_coin],
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_MESSAGE[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_MESSAGE[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'trade',
             trade_message.DEFAULT_TRADE_MESSAGE[OrderSchema.margin_coin],
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'wallet',
             wallet_message.DEFAULT_WALLET_MESSAGE[OrderSchema.margin_coin],
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin]),
        ],
        indirect=['wss'],
    )
    def test__lookup_table(self, wss: BinanceWssApi, subscr_name, message, expect):
        assert wss._lookup_table(message) == expect

    @pytest.mark.parametrize(
        'wss, status, expect', [('tbinance_spot', 'NEW', 'insert'),
                                ('tbinance_margin', 'NEW', 'insert'),
                                ('tbinance_margin_coin', 'NEW', 'insert'),
                                ('tbinance_spot', 'FILLED', 'delete'),
                                ('tbinance_spot', 'CANCELED', 'delete'),
                                ('tbinance_spot', 'EXPIRED', 'delete'),
                                ('tbinance_spot', 'REJECTED', 'delete'),
                                ('tbinance_margin', 'FILLED', 'delete'),
                                ('tbinance_margin', 'CANCELED', 'delete'),
                                ('tbinance_margin', 'EXPIRED', 'delete'),
                                ('tbinance_margin', 'REJECTED', 'delete'),
                                ('tbinance_margin_coin', 'FILLED', 'delete'),
                                ('tbinance_margin_coin', 'CANCELED', 'delete'),
                                ('tbinance_margin_coin', 'EXPIRED', 'delete'),
                                ('tbinance_margin_coin', 'REJECTED', 'delete'),
                                ('tbinance_spot', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_spot', 'NEW_INSURANCE', 'update'),
                                ('tbinance_spot', 'NEW_ADL', 'update'),
                                ('tbinance_margin', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_margin', 'NEW_INSURANCE', 'update'),
                                ('tbinance_margin', 'NEW_ADL', 'update'),
                                ('tbinance_margin_coin', 'PARTIALLY_FILLED', 'update'),
                                ('tbinance_margin_coin', 'NEW_INSURANCE', 'update'),
                                ('tbinance_margin_coin', 'NEW_ADL', 'update')],
        indirect=['wss'],
    )
    def test_define_action_by_order_status(self, wss: BinanceWssApi, status, expect):
        assert wss.define_action_by_order_status(status) == expect

    @pytest.mark.parametrize(
        'wss, message, expect', [
            ('tbinance_spot',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_spot',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange]),
            ('tbinance_margin',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.margin],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.margin]),
            ('tbinance_margin_coin',
             order_message.DEFAULT_ORDER_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             order_book_message.DEFAULT_ORDER_BOOK_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             position_message.DEFAULT_POSITION_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             quote_message.DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             symbol_message.DEFAULT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             symbol_message.DEFAULT_SYMBOL_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             trade_message.DEFAULT_TRADE_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin',
             wallet_message.DEFAULT_WALLET_LOOKUP_TABLE_RESULT[OrderSchema.margin_coin],
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin]),
        ],
        indirect=['wss'],
    )
    def test__split_message(self, wss: BinanceWssApi, message, expect):
        assert wss._split_message(deepcopy(message)) == expect

    @classmethod
    def init_partial_state(cls, wss: BinanceWssApi, subscr_name):
        schema = wss.schema
        if schema in (OrderSchema.margin, OrderSchema.margin_coin) and subscr_name == 'position':
            leverage_brackets, position_state = get_position_partial_state_data(schema)
            wss.partial_state_data[subscr_name].update({
                'position_state': position_state,
                'leverage_brackets': leverage_brackets,
            })
        if schema in (OrderSchema.margin_cross, OrderSchema.margin,
                      OrderSchema.margin_coin) and subscr_name == 'wallet':
            wss.partial_state_data[subscr_name].update({
                'wallet_state': deepcopy(wallet_message.DEFAULT_WALLET_STATE[schema])
            })
        if schema in (OrderSchema.margin_cross, OrderSchema.margin) and subscr_name == 'wallet_extra':
            wss.partial_state_data[subscr_name].update({
                'wallet_extra_state': deepcopy(wallet_message.DEFAULT_WALLET_EXTRA_STATE[schema])
            })

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
            ('tbinance_spot', 'wallet',
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.exchange],
             wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.exchange]),
            ('tbinance_margin', 'order',
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             order_message.DEFAULT_ORDER_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             order_book_message.DEFAULT_ORDER_BOOK_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'position',
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             position_message.DEFAULT_POSITION_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'position',
             position_message.DEFAULT_POSITION_DETAIL_MESSAGES[OrderSchema.margin],
             position_message.DEFAULT_POSITION_DETAIL_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             quote_message.DEFAULT_QUOTE_BIN_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             symbol_message.DEFAULT_SYMBOL_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'trade',
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             trade_message.DEFAULT_TRADE_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'wallet',
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin', 'wallet_extra',
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.margin],
             wallet_message.DEFAULT_WALLET_EXTRA_GET_DATA_RESULT[OrderSchema.margin]),
            ('tbinance_margin_coin', 'order',
             order_message.DEFAULT_ORDER_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             order_message.DEFAULT_ORDER_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'order_book',
             order_book_message.DEFAULT_ORDER_BOOK_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             order_book_message.DEFAULT_ORDER_BOOK_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'position',
             position_message.DEFAULT_POSITION_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             position_message.DEFAULT_POSITION_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'position',
             position_message.DEFAULT_POSITION_DETAIL_MESSAGES[OrderSchema.margin_coin],
             position_message.DEFAULT_POSITION_DETAIL_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'quote_bin',
             quote_message.DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             quote_message.DEFAULT_QUOTE_BIN_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_DETAIL_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'symbol',
             symbol_message.DEFAULT_SYMBOL_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             symbol_message.DEFAULT_SYMBOL_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'trade',
             trade_message.DEFAULT_TRADE_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             trade_message.DEFAULT_TRADE_GET_DATA_RESULT[OrderSchema.margin_coin]),
            ('tbinance_margin_coin', 'wallet',
             wallet_message.DEFAULT_WALLET_SPLIT_MESSAGE_RESULT[OrderSchema.margin_coin],
             wallet_message.DEFAULT_WALLET_GET_DATA_RESULT[OrderSchema.margin_coin])
        ],
        indirect=['wss'],
    )
    async def test_get_data(self, wss: BinanceWssApi, subscr_name, messages, expect):
        self.init_partial_state(wss, subscr_name)
        for message in messages:
            assert await wss.get_data(deepcopy(message)) == {}

        self.init_partial_state(wss, subscr_name)
        wss._subscriptions = {subscr_name: {'*': {'1'}}}
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

    def validate_messages(self, subscr_name):
        for message in self.messages:
            header = message[subscr_name]
            assert Schema(fields.WS_MESSAGE_HEADER_FIELDS).validate(header) == header
            for data in header['d']:
                assert Schema(fields.WS_MESSAGE_DATA_FIELDS[subscr_name]).validate(data) == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'wss_auth, subscr_name, symbol', [
            ('tbinance_spot', 'order_book', 'BTCUSDT'), ('tbinance_spot', 'order_book', None),
            ('tbinance_spot', 'quote_bin', 'BTCUSDT'), ('tbinance_spot', 'quote_bin', None),
            ('tbinance_spot', 'symbol', 'BTCUSDT'), ('tbinance_spot', 'symbol', None),
            ('tbinance_spot', 'trade', 'BTCUSDT'), ('tbinance_spot', 'trade', None),
            ('tbinance_spot', 'wallet', None),
            ('tbinance_spot', 'order', 'BTCUSDT'), ('tbinance_spot', 'order', None),
            ('tbinance_margin', 'order_book', 'BTCUSDT'), ('tbinance_margin', 'order_book', None),
            ('tbinance_margin', 'quote_bin', 'BTCUSDT'), ('tbinance_margin', 'quote_bin', None),
            ('tbinance_margin', 'symbol', 'BTCUSDT'), ('tbinance_margin', 'symbol', None),
            ('tbinance_margin', 'trade', 'BTCUSDT'), ('tbinance_margin', 'trade', None),
            ('tbinance_margin', 'wallet', None),
            ('tbinance_margin', 'order', 'BTCUSDT'), ('tbinance_margin', 'order', None),
            ('tbinance_margin', 'position', 'BTCUSDT'), ('tbinance_margin', 'position', None),
            ('tbinance_margin_coin', 'order_book', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'order_book', None),
            ('tbinance_margin_coin', 'quote_bin', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'quote_bin', None),
            ('tbinance_margin_coin', 'symbol', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'symbol', None),
            ('tbinance_margin_coin', 'trade', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'trade', None),
            ('tbinance_margin_coin', 'wallet', None),
            ('tbinance_margin_coin', 'order', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'order', None),
            ('tbinance_margin_coin', 'position', 'BTCUSD_PERP'), ('tbinance_margin_coin', 'position', None)
        ], indirect=['wss_auth'],
    )
    async def test_subscription(self, wss_auth: BinanceWssApi, subscr_name, symbol: Optional[str]):
        subscr_channel = '1'
        self.reset()
        await self.subscribe(wss_auth, subscr_channel, subscr_name, symbol)
        self.validate_messages(subscr_name)
        self.reset()
        assert wss_auth._subscriptions == {subscr_name: {f"{symbol or '*'}".lower(): {subscr_channel}}}
        assert await wss_auth.unsubscribe(subscr_channel, subscr_name, symbol)
        assert wss_auth._subscriptions == {}
