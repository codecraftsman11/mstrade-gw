# pylint: disable=no-self-use
import logging
import pytest
from mst_gateway.connector.api.bitmex.rest import BitmexRestApi
from mst_gateway.exceptions import ConnectorError
from mst_gateway.logging import init_logger
import tests.config as cfg


@pytest.fixture
def _bitmex(_debug) -> BitmexRestApi:
    yield BitmexRestApi(url=cfg.BITMEX_URL,
                        auth={
                            'api_key': cfg.BITMEX_API_KEY,
                            'api_secret': cfg.BITMEX_API_SECRET
                        },
                        logger=_debug)


@pytest.fixture
def _bitmex_unauth(_debug) -> BitmexRestApi:
    yield BitmexRestApi(url=cfg.BITMEX_URL,
                        auth={
                            'api_key': None,
                            'api_secret': None
                        },
                        logger=_debug)


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


class TestBitmexRestApi:
    def test_unauth_get_user(self, _bitmex_unauth: BitmexRestApi):
        with pytest.raises(ConnectorError):
            _bitmex_unauth.open()
            _bitmex_unauth.get_user()

    def test_get_user(self, _bitmex: BitmexRestApi):
        result = _bitmex.get_user()
        assert result['username'] == "belka158@gmail.com"

    def test_list_symbols(self, _bitmex: BitmexRestApi):
        assert cfg.BITMEX_SYMBOL in _bitmex.list_symbols()

    def test_get_quote(self, _bitmex: BitmexRestApi):
        assert set(_bitmex.get_quote(symbol=cfg.BITMEX_SYMBOL)[0].keys()) == set([
            "timestamp",
            "symbol",
            "side",
            "size",
            "price",
            "tickDirection",
            "trdMatchID",
            "grossValue",
            "homeNotional",
            "foreignNotional"
        ])
