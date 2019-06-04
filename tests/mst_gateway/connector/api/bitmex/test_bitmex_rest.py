# pylint: disable=no-self-use
import logging
import pytest
from mst_gateway.connector.api.bitmex.rest import BitmexRestApi
from mst_gateway.exceptions import ConnectorError
from mst_gateway.logging import init_logger
from mst_gateway.connector import api
from mst_gateway.utils import generate_order_id
import tests.config as cfg
from tests.utils import data_valid


@pytest.fixture
def _bitmex(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug) as bitmex:
        bitmex.open()
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_keepalive_compress(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug) as bitmex:
        bitmex.open(keepalive=True, compress=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_keepalive(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug) as bitmex:
        bitmex.open(keepalive=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_compress(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug) as bitmex:
        bitmex.open(compress=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_unauth(_debug) -> BitmexRestApi:
    with BitmexRestApi(url=cfg.BITMEX_URL,
                       auth={
                           'api_key': None,
                           'api_secret': None
                       },
                       logger=_debug) as bitmex:
        bitmex.open()
        yield bitmex


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


class TestBitmexRestApi:
    def test_get_user(self, _bitmex: BitmexRestApi):
        result = _bitmex.get_user()
        assert result['username'] == cfg.BITMEX_USERNAME
        assert result['email'] == cfg.BITMEX_EMAIL
        assert result['preferences']['locale'] == cfg.BITMEX_LOCALE

    def test_list_symbols(self, _bitmex: BitmexRestApi,
                          _bitmex_unauth: BitmexRestApi):
        assert data_valid(_bitmex.list_symbols().pop(), cfg.SYMBOL_FIELDS)
        assert data_valid(_bitmex_unauth.list_symbols().pop(), cfg.SYMBOL_FIELDS)

    def test_list_quotes(self, _bitmex: BitmexRestApi,
                         _bitmex_unauth: BitmexRestApi):
        assert data_valid(_bitmex.list_quotes(symbol=cfg.BITMEX_SYMBOL).pop(), cfg.QUOTE_FIELDS)
        assert data_valid(_bitmex_unauth.list_quotes(symbol=cfg.BITMEX_SYMBOL).pop(), cfg.QUOTE_FIELDS)

    def test_list_quote_bins(self, _bitmex: BitmexRestApi):
        quote_bins = _bitmex.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                             binsize='1m', count=1000)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert data_valid(quote_bins[0], cfg.QUOTE_BIN_FIELDS)

    def test_list_quote_bins_keepalive_compress(self, _bitmex_keepalive_compress: BitmexRestApi):
        quote_bins = _bitmex_keepalive_compress.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                                binsize='1m',
                                                                count=1000)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert data_valid(quote_bins[0], cfg.QUOTE_BIN_FIELDS)

    def test_list_quote_bins_keepalive(self, _bitmex_keepalive: BitmexRestApi):
        quote_bins = _bitmex_keepalive.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                       binsize='1m', count=1000)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert data_valid(quote_bins[0], cfg.QUOTE_BIN_FIELDS)

    def test_list_quote_bins_compress(self, _bitmex_compress: BitmexRestApi):
        quote_bins = _bitmex_compress.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                      binsize='1m', count=1000)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert data_valid(quote_bins[0], cfg.QUOTE_BIN_FIELDS)

    def test_create_order(self, _bitmex: BitmexRestApi):
        assert _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                                    side=api.BUY,
                                    order_type=api.MARKET)

    def test_list_orders(self, _bitmex: BitmexRestApi):
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.MARKET)
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.MARKET)
        assert _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL, active_only=False,
                                   options={'count': 1})

    def test_get_order(self, _bitmex: BitmexRestApi, _debug: logging.Logger):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.MARKET,
                             order_id=order_id)
        order = _bitmex.get_order(order_id=order_id)
        assert data_valid(order, cfg.ORDER_FIELDS)
        assert order['symbol'] == cfg.BITMEX_SYMBOL

    def test_close_order(self, _bitmex: BitmexRestApi):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.MARKET,
                             order_id=order_id)
        _bitmex.close_order(order_id)
        assert not _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL)

    def test_close_all_orders(self, _bitmex: BitmexRestApi):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.MARKET,
                             order_id=order_id)
        assert _bitmex.get_order(order_id=order_id)
        _bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)
        assert _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL) == []

    def test_unauth_get_user_exception(self, _bitmex_unauth: BitmexRestApi):
        with pytest.raises(ConnectorError):
            _bitmex_unauth.get_user()
