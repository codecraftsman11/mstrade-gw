import logging
import asyncio
import pytest
from websockets.client import WebSocketClientProtocol
from mst_gateway.logging import init_logger
from mst_gateway.connector.api import schema
from mst_gateway.connector.api.stocks.bitmex import BitmexWssApi
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
import tests.config as cfg


# pylint: disable=invalid-name
pytestmark = pytest.mark.asyncio


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


class TestBitmexWssApi:

    async def test_bitmex_wss_auth_client(self, _wss_api: BitmexWssApi):
        async def authenticate():
            try:
                await _wss_api.open()
                return await _wss_api.authenticate()
            finally:
                await _wss_api.close()

        assert await authenticate()

    async def test_bitmex_wss_symbol(self, _wss_api: BitmexWssApi):
        async def subscribe():
            try:
                _wss = await _wss_api.open()
                await _wss_api.subscribe('symbol')
                t1: asyncio.Task = asyncio.create_task(consume(_wss_api, _wss, self.on_message))
                await asyncio.sleep(10)
                t1.cancel()
            finally:
                await _wss_api.close()

        self.reset()
        await subscribe()
        assert self.data
        assert schema.data_update_valid(self.data[-1], schema.SYMBOL_FIELDS)

    def on_message(self, data):
        self.data.append(data)

    def reset(self):
        # pylint: disable=attribute-defined-outside-init
        self.data = []
