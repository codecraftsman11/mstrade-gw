# pylint: disable=no-self-use
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import logging
import pytest
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
from mst_gateway.exceptions import ConnectorError
from mst_gateway.logging import init_logger
from mst_gateway.connector import api
from mst_gateway.connector.api import schema
from mst_gateway.utils import generate_order_id
from mst_gateway.connector.api.stocks.bitmex.utils import (
    calc_face_price,
    calc_price
)
import tests.config as cfg
from .data.storage import STORAGE_DATA


TEST_FROM_DATE = datetime.now(tz=timezone.utc) - timedelta(days=2)
TEST_RANGE_TO_DATE = TEST_FROM_DATE + timedelta(minutes=1)
TEST_TO_DATE = datetime.now(tz=timezone.utc)


@pytest.fixture
def _bitmex(_debug) -> BitmexRestApi:
    with BitmexRestApi(name=cfg.BITMEX_NAME,
                       url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug['logger'],
                       state_storage=STORAGE_DATA) as bitmex:
        bitmex.open()
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_keepalive_compress(_debug) -> BitmexRestApi:
    with BitmexRestApi(name=cfg.BITMEX_NAME,
                       url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug,
                       state_storage=STORAGE_DATA) as bitmex:
        bitmex.open(keepalive=True, compress=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_keepalive(_debug) -> BitmexRestApi:
    with BitmexRestApi(name=cfg.BITMEX_NAME,
                       url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug,
                       state_storage=STORAGE_DATA) as bitmex:
        bitmex.open(keepalive=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_compress(_debug) -> BitmexRestApi:
    with BitmexRestApi(name=cfg.BITMEX_NAME,
                       url=cfg.BITMEX_URL,
                       auth={
                           'api_key': cfg.BITMEX_API_KEY,
                           'api_secret': cfg.BITMEX_API_SECRET
                       },
                       logger=_debug,
                       state_storage=STORAGE_DATA) as bitmex:
        bitmex.open(compress=True)
        yield bitmex
        bitmex.cancel_all_orders()
        bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)


@pytest.fixture
def _bitmex_unauth(_debug) -> BitmexRestApi:
    with BitmexRestApi(name=cfg.BITMEX_NAME,
                       url=cfg.BITMEX_URL,
                       auth={
                           'api_key': None,
                           'api_secret': None
                       },
                       logger=_debug,
                       state_storage=STORAGE_DATA) as bitmex:
        bitmex.open()
        yield bitmex


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


class TestBitmexRestApi:
    # pylint: disable=too-many-public-methods
    def test_bitmex_rest_client_single(self, _bitmex: BitmexRestApi):
        assert True

    def test_bitmex_rest_client_scope(self, _bitmex: BitmexRestApi,
                                      _bitmex_unauth: BitmexRestApi):
        assert True

    def test_bitmex_rest_get_user(self, _bitmex: BitmexRestApi):
        assert schema.data_valid(_bitmex.get_user(), schema.USER_FIELDS)

    def test_bitmex_rest_list_symbols(self, _bitmex: BitmexRestApi,
                                      _bitmex_unauth: BitmexRestApi):
        _symbol = None
        for symbol in _bitmex.list_symbols(schema=cfg.BITMEX_SCHEMA):
            if symbol.get('symbol').lower() == cfg.BITMEX_SYMBOL.lower():
                _symbol = symbol
                break
        assert schema.data_valid(_symbol, schema.SYMBOL_FIELDS)
        for symbol in _bitmex_unauth.list_symbols(schema=cfg.BITMEX_SCHEMA):
            if symbol.get('symbol').lower() == cfg.BITMEX_SYMBOL.lower():
                _symbol = symbol
                break
        assert schema.data_valid(_symbol, schema.SYMBOL_FIELDS)

    def test_bitmex_rest_list_quotes(self, _bitmex: BitmexRestApi,
                                     _bitmex_unauth: BitmexRestApi):
        assert schema.data_valid(_bitmex.list_quotes(symbol=cfg.BITMEX_SYMBOL).pop(),
                                 schema.QUOTE_FIELDS)
        assert schema.data_valid(_bitmex_unauth.list_quotes(symbol=cfg.BITMEX_SYMBOL).pop(),
                                 schema.QUOTE_FIELDS)

    def test_bitmex_rest_list_quotes_range(self, _bitmex: BitmexRestApi):
        res_data = _bitmex.list_quotes(
            symbol=cfg.BITMEX_SYMBOL,
            date_from=TEST_FROM_DATE,
            date_to=TEST_TO_DATE,
            count=10
        )
        assert len(res_data) == 10
        assert res_data[0]['time'] > TEST_FROM_DATE
        assert res_data[-1]['time'] < TEST_TO_DATE

    def test_bitmex_rest_list_quote_bins(self, _bitmex: BitmexRestApi):
        quote_bins = _bitmex.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                             schema=cfg.BITMEX_SCHEMA,
                                             binsize='1m', count=1000, state_data=STORAGE_DATA)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert schema.data_valid(quote_bins[0], schema.QUOTE_BIN_FIELDS)

    def test_bitmex_rest_list_quote_bins_range(self, _bitmex: BitmexRestApi):
        res_data = _bitmex.list_quote_bins(
            symbol=cfg.BITMEX_SYMBOL,
            schema=cfg.BITMEX_SCHEMA,
            binsize='1m',
            count=1000,
            date_from=TEST_FROM_DATE,
            date_to=TEST_RANGE_TO_DATE,
            state_data=STORAGE_DATA
        )
        assert len(res_data) < 1000
        assert res_data[0]['time'] > TEST_FROM_DATE
        assert res_data[-1]['time'] < TEST_RANGE_TO_DATE

    def test_bitmex_rest_list_quote_bins_keepalive_compress(self, _bitmex_keepalive_compress: BitmexRestApi):
        quote_bins = _bitmex_keepalive_compress.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                                schema=cfg.BITMEX_SCHEMA,
                                                                binsize='1m',
                                                                count=1000,
                                                                state_data=STORAGE_DATA)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert schema.data_valid(quote_bins[0], schema.QUOTE_BIN_FIELDS)

    def test_bitmex_rest_list_quote_bins_keepalive(self, _bitmex_keepalive: BitmexRestApi):
        quote_bins = _bitmex_keepalive.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                       schema=cfg.BITMEX_SCHEMA,
                                                       binsize='1m', count=1000,
                                                       state_data=STORAGE_DATA)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert schema.data_valid(quote_bins[0], schema.QUOTE_BIN_FIELDS)

    def test_bitmex_rest_list_quote_bins_compress(self, _bitmex_compress: BitmexRestApi):
        quote_bins = _bitmex_compress.list_quote_bins(symbol=cfg.BITMEX_SYMBOL,
                                                      schema=cfg.BITMEX_SCHEMA,
                                                      binsize='1m', count=1000,
                                                      state_data=STORAGE_DATA)
        assert quote_bins
        assert isinstance(quote_bins, list)
        assert len(quote_bins) == 1000
        assert schema.data_valid(quote_bins[0], schema.QUOTE_BIN_FIELDS)

    def test_bitmex_rest_create_order(self, _bitmex: BitmexRestApi):
        assert _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                                    side=api.BUY,
                                    order_type=api.OrderType.market)

    def test_bitmex_rest_list_orders(self, _bitmex: BitmexRestApi):
        o_1 = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_id=o_1,
                             order_type=api.OrderType.market)
        o_2 = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_id=o_2,
                             order_type=api.OrderType.market)
        l_1 = _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL,
                                  active_only=False,
                                  count=1, offset=1)
        l_2 = _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL,
                                  active_only=False,
                                  count=1)
        assert len(l_1) == 1
        assert l_1[0]['order_id'] == o_1
        assert len(l_2) == 1
        assert l_2[0]['order_id'] == o_2

    def test_bitmex_rest_get_order(self, _bitmex: BitmexRestApi, _debug: logging.Logger):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.OrderType.market,
                             order_id=order_id)
        order = _bitmex.get_order(order_id=order_id)
        assert schema.data_valid(order, schema.ORDER_FIELDS)
        assert order['symbol'] == cfg.BITMEX_SYMBOL

    def test_bitmex_rest_close_order(self, _bitmex: BitmexRestApi):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.OrderType.market,
                             order_id=order_id)
        _bitmex.close_order(order_id)
        assert not _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL)

    def test_bitmex_rest_close_all_orders(self, _bitmex: BitmexRestApi):
        order_id = generate_order_id()
        _bitmex.create_order(symbol=cfg.BITMEX_SYMBOL,
                             side=api.BUY,
                             order_type=api.OrderType.market,
                             order_id=order_id)
        assert _bitmex.get_order(order_id=order_id)
        _bitmex.close_all_orders(symbol=cfg.BITMEX_SYMBOL)
        assert _bitmex.list_orders(symbol=cfg.BITMEX_SYMBOL) == []

    def test_bitmex_rest_list_order_book(self, _bitmex: BitmexRestApi):
        ob_items = _bitmex.list_order_book(symbol=cfg.BITMEX_SYMBOL, schema=cfg.BITMEX_SCHEMA)
        assert ob_items
        assert isinstance(ob_items, list)
        assert schema.data_valid(ob_items[0], schema.ORDER_BOOK_FIELDS)

    def test_bitmex_rest_list_order_book_range(self, _bitmex: BitmexRestApi):
        ob_items = _bitmex.list_order_book(
            symbol=cfg.BITMEX_SYMBOL,
            schema=cfg.BITMEX_SCHEMA,
            depth=5
        )
        assert len(ob_items) == 10
        assert ob_items[0]['side'] == api.SELL
        assert ob_items[9]['side'] == api.BUY

    def test_bitmex_rest_list_order_book_split(self, _bitmex: BitmexRestApi):
        ob_items = _bitmex.list_order_book(
            symbol=cfg.BITMEX_SYMBOL,
            schema=cfg.BITMEX_SCHEMA,
            depth=5,
            split=True
        )
        assert len(ob_items[api.BUY]) == 5
        assert len(ob_items[api.SELL]) == 5
        assert ob_items[api.BUY][0]['side'] == api.BUY
        assert ob_items[api.SELL][0]['side'] == api.SELL

    def test_bitmex_rest_list_order_book_offset(self, _bitmex: BitmexRestApi):
        ob_items = _bitmex.list_order_book(
            symbol=cfg.BITMEX_SYMBOL,
            schema=cfg.BITMEX_SCHEMA,
            depth=1,
            split=True,
            offset=10
        )
        assert len(ob_items[api.BUY]) == 1
        assert len(ob_items[api.SELL]) == 1
        assert abs(ob_items[api.SELL][0]['price'] - ob_items[api.BUY][0]['price']) > 5

    def test_bitmex_rest_unauth_get_user_exception(self, _bitmex_unauth: BitmexRestApi):
        with pytest.raises(ConnectorError):
            _bitmex_unauth.get_user()

    def test_bitmex_rest_list_trades(self, _bitmex: BitmexRestApi,
                                     _bitmex_unauth: BitmexRestApi):
        assert schema.data_valid(_bitmex.list_trades(symbol=cfg.BITMEX_SYMBOL, schema=cfg.BITMEX_SCHEMA).pop(),
                                 schema.TRADE_FIELDS)
        assert schema.data_valid(_bitmex_unauth.list_trades(symbol=cfg.BITMEX_SYMBOL, schema=cfg.BITMEX_SCHEMA).pop(),
                                 schema.TRADE_FIELDS)

    def test_bitmex_rest_get_wallet(self, _bitmex: BitmexRestApi):
        data = _bitmex.get_wallet()
        assert schema.data_valid(data['balances'].pop(), schema.WALLET_MARGIN1_FIELDS)

    def test_bitmex_calc_face_price(self):
        price = 3
        assert calc_face_price('XBTUSD', price) == (1 / price, True)
        assert calc_face_price('XBTH20', price) == (1 / price, True)
        assert calc_face_price('XBTM20', price) == (1 / price, True)
        assert calc_face_price('XBT7D_U105', price) == (0.1 * price, False)
        assert calc_face_price('XBT7D_D95', price) == (0.1 * price, False)
        assert calc_face_price('ADAH20', price) == (price, False)
        assert calc_face_price('BCHH20', price) == (price, False)
        assert calc_face_price('EOSH20', price) == (price, False)
        assert calc_face_price('ETHUSD', price) == (1e-6 * price, False)
        assert calc_face_price('ETHH20', price) == (price, False)
        assert calc_face_price('LTCH20', price) == (price, False)
        assert calc_face_price('TRXH20', price) == (price, False)
        assert calc_face_price('XRPH20', price) == (price, False)
        assert calc_face_price('XBTEUR', price) == (None, None)
        assert calc_face_price('XBTUSD', 0) == (None, None)

    def test_bitmex_calc_price(self):
        price = 3
        assert calc_price('XBTUSD', price) == 1 / price
        assert calc_price('XBTH20', price) == 1 / price
        assert calc_price('XBTM20', price) == 1 / price
        assert calc_price('XBT7D_U105', price) == price * 10
        assert calc_price('XBT7D_D95', price) == price * 10
        assert calc_price('ADAH20', price) == price
        assert calc_price('BCHH20', price) == price
        assert calc_price('EOSH20', price) == price
        assert calc_price('ETHUSD', price) == 1e+6 * price
        assert calc_price('ETHH20', price) == price
        assert calc_price('LTCH20', price) == price
        assert calc_price('TRXH20', price) == price
        assert calc_price('XRPH20', price) == price
        assert calc_price('XBTEUR', price) is None
        assert calc_price('XBTUSD', 0) is None
