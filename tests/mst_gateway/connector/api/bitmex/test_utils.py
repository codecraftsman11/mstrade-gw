# pylint: disable=no-self-use
import logging
import pytest
from mst_gateway.logging import init_logger
from mst_gateway.connector.api.stocks.bitmex import utils
from mst_gateway.connector.api import BUY, SELL
from . import data

TEST_VOLUME = 10000
TEST_FILTER_DATA_BUY = [_v for _v in data.TEST_ORDER_BOOK_SPLIT_DATA[BUY] if
                        _v['volume'] >= TEST_VOLUME]
TEST_FILTER_DATA_SELL = [_v for _v in data.TEST_ORDER_BOOK_SPLIT_DATA[SELL] if
                         _v['volume'] >= TEST_VOLUME]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


class TestBitmexUtils:

    def test_bitmex_utils_split_order_book(self):
        assert data.TEST_ORDER_BOOK_SPLIT_DATA == utils.split_order_book(
            data.TEST_ORDER_BOOK_DATA,
            state_data=data.TEST_ORDER_BOOK_STATE_DATA)

    def test_bitmex_utils_filter_order_book(self):
        assert {
            BUY: TEST_FILTER_DATA_BUY,
            SELL: TEST_FILTER_DATA_SELL
        } == utils.filter_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                     min_volume_buy=TEST_VOLUME,
                                     min_volume_sell=TEST_VOLUME)

        assert {
            BUY: TEST_FILTER_DATA_BUY,
            SELL: data.TEST_ORDER_BOOK_SPLIT_DATA[SELL]
        } == utils.filter_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                     min_volume_buy=TEST_VOLUME)

        assert {
            BUY: data.TEST_ORDER_BOOK_SPLIT_DATA[BUY],
            SELL: TEST_FILTER_DATA_SELL,
        } == utils.filter_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                     min_volume_sell=TEST_VOLUME)

    def test_bitmex_utils_slice_order_book(self):
        assert {
            BUY: data.TEST_ORDER_BOOK_SPLIT_DATA[BUY][2:],
            SELL: data.TEST_ORDER_BOOK_SPLIT_DATA[SELL][:-2]
        } == utils.slice_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                    depth=None,
                                    offset=2)
        assert {
            BUY: data.TEST_ORDER_BOOK_SPLIT_DATA[BUY][2:3],
            SELL: data.TEST_ORDER_BOOK_SPLIT_DATA[SELL][-3:-2]
        } == utils.slice_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                    depth=1,
                                    offset=2)

        assert {
            BUY: data.TEST_ORDER_BOOK_SPLIT_DATA[BUY][:2],
            SELL: data.TEST_ORDER_BOOK_SPLIT_DATA[SELL][-2:]
        } == utils.slice_order_book(data.TEST_ORDER_BOOK_SPLIT_DATA,
                                    depth=2,
                                    offset=None)
