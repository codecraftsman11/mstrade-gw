# pylint: disable=invalid-name,no-self-use
import json
import logging
import asyncio
import pytest
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed
from mst_gateway.logging import init_logger
from mst_gateway.connector.api import schema
from mst_gateway.connector.api.stocks.bitmex import BitmexWssApi
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
from mst_gateway.connector.api.stocks.bitmex.utils import _date
from mst_gateway.connector.api.stocks.bitmex.wss import utils
from mst_gateway.connector.api.stocks.bitmex.wss import serializers
from mst_gateway.connector.api.stocks.bitmex.wss.router import BitmexWssRouter
import tests.config as cfg
from .data import TEST_QUOTE_BIN_MESSAGES
from .data import TEST_ORDER_BOOK_MESSAGES
from .data import TEST_SYMBOL_MESSAGES


@pytest.fixture
def _rest(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug['logger']) as rest:
        rest.open()
        yield rest
        rest.cancel_all_orders()
        rest.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _wss_api(_debug) -> BitmexWssApi:
    with BitmexWssApi(url=cfg.BITMEX_WSS_URL,
                      auth={
                          'api_key': cfg.BITMEX_API_KEY,
                          'api_secret': cfg.BITMEX_API_SECRET
                      },
                      logger=_debug['logger']) as wss:
        yield wss


@pytest.fixture
def _wss_trade_api(_debug) -> BitmexWssApi:
    with BitmexWssApi(url=cfg.BITMEX_WSS_URL,
                      auth={
                          'api_key': cfg.BITMEX_API_KEY,
                          'api_secret': cfg.BITMEX_API_SECRET
                      },
                      logger=_debug['logger'],
                      options={'use_trade_bin': False}) as wss:
        yield wss


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


async def consume(_wss_api: BitmexWssApi, wss: WebSocketClientProtocol,
                  on_message: callable):
    while True:
        try:
            message = await wss.recv()
        except ConnectionClosed:
            message = None
            wss = await _wss_api.open(restore=True)
        if message and await _wss_api.process_message(message, on_message):
            return


class TestBitmexWssApi:

    def test_bitmex_wss_parse_message(self):
        for test in TEST_SYMBOL_MESSAGES:
            assert utils.parse_message(test['message']) == json.loads(test['message'])

    def test_bitmex_wss_register_all(self, _wss_api: BitmexWssApi):
        assert not _wss_api.is_registered("symbol")
        assert not _wss_api.is_registered("symbol", "XBTUSD")
        _wss_api.register("symbol")
        assert _wss_api.is_registered("symbol")
        assert _wss_api.is_registered("symbol", "XBTUSD")
        _wss_api.unregister("symbol")
        assert not _wss_api.is_registered("symbol")
        assert not _wss_api.is_registered("symbol", "XBTUSD")

    def test_bitmex_wss_register_symbol(self, _wss_api: BitmexWssApi):
        assert not _wss_api.is_registered("symbol")
        assert not _wss_api.is_registered("symbol", "XBTUSD")
        _wss_api.register("symbol", "XBTUSD")
        assert not _wss_api.is_registered("symbol")
        assert _wss_api.is_registered("symbol", "XBTUSD")
        _wss_api.unregister("symbol", "XBTUSD")
        assert not _wss_api.is_registered("symbol")
        assert not _wss_api.is_registered("symbol", "XBTUSD")
        _wss_api.register("symbol", "XBTUSD")
        _wss_api.unregister("symbol")
        assert not _wss_api.is_registered("symbol")
        assert not _wss_api.is_registered("symbol", "XBTUSD")

    def test_bitmex_wss_router(self, _wss_api: BitmexWssApi):
        assert isinstance(_wss_api.router, BitmexWssRouter)

    def test_bitmex_wss_router_get_symbol_serializer(self, _wss_api: BitmexWssApi):
        # pylint: disable=protected-access
        _wss_api.register("symbol")
        router = _wss_api.router
        srlz1 = router._get_serializer(TEST_SYMBOL_MESSAGES[0]['message'])
        srlz2 = router._get_serializer(TEST_SYMBOL_MESSAGES[2]['message'])
        assert isinstance(srlz1, serializers.BitmexSymbolSerializer)
        assert not router._get_serializer(TEST_SYMBOL_MESSAGES[1]['message'])
        assert isinstance(srlz2, serializers.BitmexSymbolSerializer)
        assert srlz1 == srlz2

    def test_bitmex_wss_router_get_quote_bin_serializer(self, _wss_api: BitmexWssApi):
        # pylint: disable=protected-access
        _wss_api.register("quote_bin")
        router = _wss_api.router
        assert not router._get_serializer(TEST_QUOTE_BIN_MESSAGES[0]['message'])
        assert not router._get_serializer(TEST_QUOTE_BIN_MESSAGES[1]['message'])
        for test in TEST_QUOTE_BIN_MESSAGES[2:]:
            assert isinstance(router._get_serializer(test['message']),
                              serializers.BitmexQuoteBinSerializer)

    def test_bitmex_wss_get_symbol_data(self, _wss_api: BitmexWssApi):
        _wss_api.register("symbol")
        for test in TEST_SYMBOL_MESSAGES:
            assert test['data'] == _wss_api.get_data(test['message'])

    def test_bitmex_wss_get_symbol_state(self, _wss_api: BitmexWssApi):
        _wss_api.register("symbol")
        for test in TEST_SYMBOL_MESSAGES:
            _wss_api.get_data(test['message'])
        assert _wss_api.get_state("symbol") == {
            'account': "bitmex.test",
            'table': "symbol",
            'action': "partial",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'pair': ["XBT", "USD"],
                    'timestamp': _date("2019-07-01T08:16:15.250Z"),
                    'price': 10933.67
                },
                {
                    'symbol': "XBTEUR",
                    'pair': ["XBT", "EUR"],
                    'timestamp': _date("2019-07-18T20:35:00.000Z"),
                    'price': 10.79
                }
            ]
        }

    def test_bitmex_wss_get_quote_bin_data(self, _wss_api: BitmexWssApi):
        _wss_api.register("quote_bin")
        for test in TEST_QUOTE_BIN_MESSAGES:
            assert test['data'] == _wss_api.get_data(test['message'])

    def test_bitmex_wss_get_quote_bin_traded_data(self, _wss_trade_api: BitmexWssApi):
        _wss_trade_api.register("quote_bin")
        for test in TEST_QUOTE_BIN_MESSAGES:
            assert test['data_trade'] == _wss_trade_api.get_data(test['message'])

    def test_bitmex_wss_get_quote_bin_state(self, _wss_api: BitmexWssApi):
        _wss_api.register("quote_bin")
        for test in TEST_QUOTE_BIN_MESSAGES:
            _wss_api.get_data(test['message'])
        assert _wss_api.get_state("quote_bin") == {
            'account': "bitmex.test",
            'table': "quote_bin",
            'action': "partial",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:59:38.326Z"),
                    'symbol': "XBTUSD",
                    'volume': 105,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339
                }
            ]
        }

    def test_bitmex_wss_router_get_order_book_serializer(self, _wss_api: BitmexWssApi):
        # pylint: disable=protected-access
        _wss_api.register("order_book", "XBTUSD")
        router = _wss_api.router
        assert not router._get_serializer(TEST_ORDER_BOOK_MESSAGES[0]['message'])
        for test in TEST_ORDER_BOOK_MESSAGES[1:]:
            assert isinstance(router._get_serializer(test['message']),
                              serializers.BitmexOrderBookSerializer)

    def test_bitmex_wss_get_order_book_data(self, _wss_api: BitmexWssApi):
        _wss_api.register("order_book", "XBTUSD")
        for test in TEST_ORDER_BOOK_MESSAGES:
            assert test['data'] == _wss_api.get_data(test['message'])

    @pytest.mark.asyncio
    async def test_bitmex_wss_auth_client(self, _wss_api: BitmexWssApi):
        async def authenticate():
            try:
                await _wss_api.open()
                return await _wss_api.authenticate()
            finally:
                await _wss_api.close()

        assert await authenticate()

    @pytest.mark.asyncio
    async def test_bitmex_wss_symbol(self, _wss_api: BitmexWssApi):
        async def subscribe():
            try:
                _wss = await _wss_api.open()
                await _wss_api.subscribe('symbol')
                await asyncio.wait_for(
                    consume(_wss_api, _wss, self.on_message),
                    timeout=5
                )
            except asyncio.TimeoutError:
                pass
            finally:
                await _wss_api.close()

        self.reset()
        await subscribe()
        assert self.data
        assert schema.data_update_valid(self.data[-1]['data'][0], schema.SYMBOL_FIELDS)

    @pytest.mark.asyncio
    async def test_bitmex_wss_order_book(self, _wss_api: BitmexWssApi):
        async def subscribe():
            try:
                _wss = await _wss_api.open()
                await _wss_api.subscribe('order_book', 'XBTUSD')
                await asyncio.wait_for(
                    consume(_wss_api, _wss, self.on_message),
                    timeout=5
                )
            except asyncio.TimeoutError:
                pass
            finally:
                await _wss_api.close()

        self.reset()
        await subscribe()
        assert self.data
        assert schema.data_update_valid(self.data[-1]['data'][0],
                                        schema.ORDER_BOOK_FIELDS)

    @pytest.mark.asyncio
    async def test_bitmex_wss_restore_connection(self, _wss_api: BitmexWssApi):
        async def subscribe():
            try:
                _wss = await _wss_api.open()
                await _wss_api.subscribe('symbol')
                await _wss.close()
                await asyncio.wait_for(
                    consume(_wss_api, _wss, self.on_message),
                    timeout=5
                )
            except asyncio.TimeoutError:
                pass
            finally:
                await _wss_api.close()

        self.reset()
        await subscribe()
        assert self.data
        assert schema.data_update_valid(self.data[-1]['data'][0], schema.SYMBOL_FIELDS)

    def on_message(self, data):
        self.data.append(data)

    def reset(self):
        # pylint: disable=attribute-defined-outside-init
        self.data = []
