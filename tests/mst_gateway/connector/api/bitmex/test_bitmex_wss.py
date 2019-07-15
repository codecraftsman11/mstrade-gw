# pylint: disable=invalid-name,no-self-use
import json
import logging
import asyncio
import pytest
from websockets.client import WebSocketClientProtocol
from mst_gateway.logging import init_logger
from mst_gateway.connector.api import schema
from mst_gateway.connector.api.stocks.bitmex import BitmexWssApi
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
from mst_gateway.connector.api.stocks.bitmex.wss import utils
from mst_gateway.connector.api.stocks.bitmex.wss import serializers
from mst_gateway.connector.api.stocks.bitmex.wss.router import BitmexWssRouter
import tests.config as cfg


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
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


async def consume(_wss_api: BitmexWssApi, wss: WebSocketClientProtocol,
                  on_message: callable):
    while True:
        message = await wss.recv()
        if await _wss_api.process_message(message, on_message):
            return

TEST_SYMBOL_MESSAGES = [
    {
        'message': '{"table":"instrument","action":"partial"}',
        'data': None,
    },
    {
        'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","fairPrice":10933.67,"markPrice":10933.67,"timestamp":"2019-07-01T08:16:15.250Z"}]}',
        'data': None
    },
    {
        'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","lastPrice":10933.67,"markPrice":10933.67,"timestamp":"2019-07-01T08:16:15.250Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'type': "update",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'timestamp': "2019-07-01T08:16:15.250Z",
                    'price': 10933.67
                }
            ]
        }
    },
]

TEST_QUOTE_BIN_MESSAGES = [
    {
        'message': '{"table":"trade","action":"partial","data":[{"timestamp":"2019-07-01T10:29:04.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': None
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:58:09.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': "2019-07-01T11:58:09.589Z",
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                }
            ]
        }
    },
    {
        'message': '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2019-07-01T11:59:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': "2019-07-01T11:59:00.000Z",
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        }
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:36.307Z","symbol":"XBTUSD","side":"Sell","size":100,"price":11329,"tickDirection":"MinusTick","trdMatchID":"4e2522dc-c411-46dc-7f2f-e33491965ddd","grossValue":882700,"homeNotional":0.008827,"foreignNotional":100}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': "2019-07-01T11:59:36.307Z",
                    'symbol': "XBTUSD",
                    'volume': 100,
                    'open': 11329,
                    'close': 11329,
                    'low': 11329,
                    'high': 11329
                }
            ]
        }
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:38.326Z","symbol":"XBTUSD","side":"Sell","size":5,"price":11339,"tickDirection":"ZeroMinusTick","trdMatchID":"1084f572-05d1-c16d-d5d3-02d5f8a9bbbb","grossValue":44135,"homeNotional":0.00044135,"foreignNotional":5}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': "2019-07-01T11:59:38.326Z",
                    'symbol': "XBTUSD",
                    'volume': 105,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339
                }
            ]
        }
    }
]


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
        assert not router._get_serializer(TEST_SYMBOL_MESSAGES[0]['message'])
        assert not router._get_serializer(TEST_SYMBOL_MESSAGES[1]['message'])
        assert isinstance(router._get_serializer(TEST_SYMBOL_MESSAGES[2]['message']),
                          serializers.BitmexSymbolSerializer)

    def test_bitmex_wss_router_get_quote_bin_serializer(self, _wss_api: BitmexWssApi):
        # pylint: disable=protected-access
        _wss_api.register("quote_bin")
        router = _wss_api.router
        assert not router._get_serializer(TEST_QUOTE_BIN_MESSAGES[0]['message'])
        for test in TEST_QUOTE_BIN_MESSAGES[1:]:
            assert isinstance(router._get_serializer(test['message']),
                              serializers.BitmexQuoteBinSerializer)

    def test_bitmex_wss_get_symbol_data(self, _wss_api: BitmexWssApi):
        _wss_api.register("symbol")
        for test in TEST_SYMBOL_MESSAGES:
            assert test['data'] == _wss_api.get_data(test['message'])

    def test_bitmex_wss_get_quote_bin_data(self, _wss_api: BitmexWssApi):
        _wss_api.register("quote_bin")
        for test in TEST_QUOTE_BIN_MESSAGES:
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

    def on_message(self, data):
        self.data.append(data)

    def reset(self):
        # pylint: disable=attribute-defined-outside-init
        self.data = []
