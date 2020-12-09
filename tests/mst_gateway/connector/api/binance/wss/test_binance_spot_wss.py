import json
import logging
import pytest
from copy import deepcopy
from mst_gateway.connector.api.stocks.binance import BinanceWssApi, var
from mst_gateway.connector.api.stocks.binance.wss import subscribers
from mst_gateway.connector.api.stocks.binance.wss.router import BinanceWssRouter
from mst_gateway.connector.api.utils import parse_message

from tests import config as cfg
from .data.storage import STORAGE_DATA

from .data.order import (
    SPOT_ORDER_MESSAGE,
    SPOT_ORDER_LOOKUP_TABLE_RESULT,
    SPOT_ORDER_SPLIT_MESSAGE_RESULTS,
    SPOT_ORDER_GET_DATA_RESULTS,
)
from .data.order_book import (
    SPOT_ORDER_BOOK_MESSAGE,
    SPOT_ORDER_BOOK_LOOKUP_TABLE_RESULT,
    SPOT_ORDER_BOOK_SPLIT_MESSAGE_RESULTS,
    SPOT_ORDER_BOOK_GET_DATA_RESULTS,
)
from .data.quote_bin import (
    SPOT_QUOTE_BIN_MESSAGE,
    SPOT_QUOTE_BIN_LOOKUP_TABLE_RESULT,
    SPOT_QUOTE_BIN_SPLIT_MESSAGE_RESULTS,
    SPOT_QUOTE_BIN_GET_DATA_RESULTS,
)
from .data.symbol import (
    SPOT_SYMBOL_DETAIL_MESSAGE,
    SPOT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT,
    SPOT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULTS,
    SPOT_SYMBOL_DETAIL_GET_DATA_RESULTS,
    SPOT_SYMBOL_MESSAGE,
    SPOT_SYMBOL_LOOKUP_TABLE_RESULT,
    SPOT_SYMBOL_SPLIT_MESSAGE_RESULTS,
    SPOT_SYMBOL_GET_DATA_RESULTS,
)
from .data.trade import (
    SPOT_TRADE_MESSAGE,
    SPOT_TRADE_LOOKUP_TABLE_RESULT,
    SPOT_TRADE_SPLIT_MESSAGE_RESULTS,
    SPOT_TRADE_GET_DATA_RESULTS,
)
from .data.wallet import (
    SPOT_WALLET_MESSAGE,
    SPOT_WALLET_LOOKUP_TABLE_RESULT,
    SPOT_WALLET_SPLIT_MESSAGE_RESULTS,
    SPOT_WALLET_GET_DATA_RESULTS,
    SPOT_PROCESS_WALLET_MESSAGE_RESULT,
)

logger = logging.getLogger(__name__)


@pytest.fixture
async def _wss_api() -> BinanceWssApi:
    with BinanceWssApi(
        url=cfg.BINANCE_WSS_API_URL,
        name=cfg.BINANCE_WSS_API_NAME,
        account_name=cfg.BINANCE_WSS_API_ACCOUNT_NAME,
        schema=cfg.BINANCE_SPOT_SCHEMA,
        auth=cfg.BINANCE_AUTH_KEYS,
        state_storage=deepcopy(STORAGE_DATA),
        logger=logger,
    ) as _wss_api:
        try:
            await _wss_api.open()
        except Exception as exc:
            logger.error(exc)
        yield _wss_api
        await _wss_api.close()


@pytest.fixture
async def _testnet_wss_api() -> BinanceWssApi:
    with BinanceWssApi(
        url=cfg.BINANCE_TESTNET_WSS_API_URL,
        name=cfg.BINANCE_WSS_API_NAME,
        account_name=cfg.BINANCE_WSS_API_ACCOUNT_NAME,
        schema=cfg.BINANCE_SPOT_SCHEMA,
        auth=cfg.BINANCE_TESTNET_AUTH_KEYS,
        state_storage=deepcopy(STORAGE_DATA),
        logger=logger,
    ) as _testnet_wss_api:
        try:
            await _testnet_wss_api.open()
        except Exception as exc:
            logger.error(exc)
        yield _testnet_wss_api
        await _testnet_wss_api.close()


class TestBinanceSpotWssApi:
    def reset(self):
        self.data = []

    def on_message(self, data):
        self.data.append(data)

    async def consume(self, wss_api, api_handler, on_message: callable):
        from websockets.exceptions import ConnectionClosed

        while True:
            try:
                message = await api_handler.recv()
                if await wss_api.process_message(message, on_message):
                    break
            except ConnectionClosed:
                api_handler = await wss_api.open(restore=True)

    async def subscribe(self, wss_api, subscr_channel, subscr_name, symbol=None):
        assert await wss_api.subscribe(subscr_channel, subscr_name, symbol)
        await self.consume(wss_api, wss_api.handler, self.on_message)

    def test_binance_wss_spot_str(self, _testnet_wss_api: BinanceWssApi):
        assert str(_testnet_wss_api) == cfg.BINANCE_WSS_API_NAME.lower()

    def test_binance_wss_spot_account_name(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.account_name == cfg.BINANCE_ACCOUNT_NAME

    def test_binance_wss_spot_account_id(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.account_id == cfg.BINANCE_ACCOUNT_ID

    def test_binance_wss_spot_url(
        self, _testnet_wss_api: BinanceWssApi, _wss_api: BinanceWssApi
    ):
        assert _testnet_wss_api._url == cfg.BINANCE_TESTNET_WSS_API_URL
        assert _wss_api._url == cfg.BINANCE_WSS_API_URL

    def test_binance_wss_spot_options(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.options == {}

    def test_binance_wss_spot_subscriptions(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.subscriptions == {}

    def test_binance_wss_spot_router(self, _testnet_wss_api: BinanceWssApi):
        assert isinstance(_testnet_wss_api.router, BinanceWssRouter)

    def test_binance_wss_spot_logger(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.logger

    def test_binance_wss_spot_handler(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.handler

    def test_binance_wss_spot_auth_data(
        self, _testnet_wss_api: BinanceWssApi, _wss_api: BinanceWssApi
    ):
        assert _testnet_wss_api.auth == cfg.BINANCE_TESTNET_AUTH_KEYS
        assert _wss_api.auth == cfg.BINANCE_AUTH_KEYS

    def test_binance_wss_spot_test(
        self, _testnet_wss_api: BinanceWssApi, _wss_api: BinanceWssApi
    ):
        assert _testnet_wss_api.test
        assert not _wss_api.test

    @pytest.mark.asyncio
    async def test_binance_wss_spot_open_auth(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.auth_connect is False
        assert not _testnet_wss_api.tasks
        await _testnet_wss_api.close()
        assert not _testnet_wss_api.handler
        assert await _testnet_wss_api.open(is_auth=True)
        assert _testnet_wss_api.auth_connect
        assert _testnet_wss_api.tasks

    @pytest.mark.parametrize(
        "subscr_name, subscriber_class",
        [
            ("order", subscribers.BinanceOrderSubscriber),
            ("order_book", subscribers.BinanceOrderBookSubscriber),
            ("quote_bin", subscribers.BinanceQuoteBinSubscriber),
            ("symbol", subscribers.BinanceSymbolSubscriber),
            ("trade", subscribers.BinanceTradeSubscriber),
            ("wallet", subscribers.BinanceWalletSubscriber),
        ],
    )
    def test_binance_wss_spot__get_subscriber(
        self, _testnet_wss_api: BinanceWssApi, subscr_name, subscriber_class
    ):
        assert isinstance(
            _testnet_wss_api._get_subscriber(subscr_name), subscriber_class
        )

    @pytest.mark.parametrize(
        "subscriptions, subscr_name, remap_result",
        [
            (
                {"symbol": {"btcusdt": {"1"}, "*": {"1"}}},
                "symbol",
                {"symbol": {"*": {"1"}}},
            ),
            (
                {"symbol": {"btcusdt": {"1"}, "*": {"2"}}},
                "symbol",
                {"symbol": {"*": {"1", "2"}}},
            ),
        ],
    )
    def test_binance_wss_spot_remap_subscriptions(
        self, _testnet_wss_api: BinanceWssApi, subscriptions, subscr_name, remap_result
    ):
        _testnet_wss_api._subscriptions = subscriptions
        assert _testnet_wss_api.remap_subscriptions(subscr_name=subscr_name) is None
        assert _testnet_wss_api._subscriptions == remap_result

    def test_binance_wss_spot_is_registered(self, _testnet_wss_api: BinanceWssApi):
        assert not _testnet_wss_api.is_registered(subscr_name="symbol")
        _testnet_wss_api._subscriptions = {"symbol": {"btcusdt": {"1"}}}
        assert _testnet_wss_api.is_registered(subscr_name="symbol", symbol="btcusdt")
        assert _testnet_wss_api.is_registered(subscr_name="SYMBOL", symbol="BTCUSDT")
        assert not _testnet_wss_api.is_registered(
            subscr_name="symbol", symbol="ethusdt"
        )
        _testnet_wss_api._subscriptions = {"symbol": {"*": {"1"}}}
        assert _testnet_wss_api.is_registered(subscr_name="symbol")
        assert _testnet_wss_api.is_registered(subscr_name="symbol", symbol="ethusdt")

    def test_binance_wss_spot_register(self, _testnet_wss_api: BinanceWssApi):
        assert _testnet_wss_api.register(
            subscr_name="symbol", symbol="btcusdt", subscr_channel="1"
        ) == (True, "btcusdt")
        assert _testnet_wss_api._subscriptions == {"symbol": {"btcusdt": {"1"}}}
        assert _testnet_wss_api.register(
            subscr_name="SYMBOL", symbol="BTCUSDT", subscr_channel="2"
        ) == (True, "btcusdt")
        assert _testnet_wss_api._subscriptions == {"symbol": {"btcusdt": {"1", "2"}}}
        assert _testnet_wss_api.register(
            subscr_name="symbol", symbol="ethusdt", subscr_channel="1"
        ) == (True, "ethusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1", "2"}, "ethusdt": {"1"}}
        }
        assert _testnet_wss_api.register(subscr_name="symbol", subscr_channel="1") == (
            True,
            "*",
        )
        assert _testnet_wss_api._subscriptions == {"symbol": {"*": {"1", "2"}}}
        assert _testnet_wss_api.register(subscr_name="symbol", subscr_channel="3") == (
            True,
            "*",
        )
        assert _testnet_wss_api._subscriptions == {"symbol": {"*": {"1", "2", "3"}}}
        assert _testnet_wss_api.register(
            subscr_name="symbol", symbol="btcusdt", subscr_channel="4"
        ) == (True, "*")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"*": {"1", "2", "3", "4"}}
        }
        assert _testnet_wss_api.register(
            subscr_name="order", symbol="btcusdt", subscr_channel="1"
        ) == (True, "btcusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"*": {"1", "2", "3", "4"}},
            "order": {"btcusdt": {"1"}},
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "subscr_name, subscr_channel, subscriptions",
        [
            ("order_book", "1", {"order_book": {"*": {"1"}}}),
            ("ORDER_BOOK", "1", {"order_book": {"*": {"1"}}}),
            ("quote_bin", "1", {"quote_bin": {"*": {"1"}}}),
            ("QUOTE_BIN", "1", {"quote_bin": {"*": {"1"}}}),
            ("symbol", "1", {"symbol": {"*": {"1"}}}),
            ("SYMBOL", "1", {"symbol": {"*": {"1"}}}),
            ("trade", "1", {"trade": {"*": {"1"}}}),
            ("TRADE", "1", {"trade": {"*": {"1"}}}),
        ],
    )
    async def test_binance_wss_spot_subscribe_public(
        self, _wss_api: BinanceWssApi, subscr_name, subscr_channel, subscriptions,
    ):
        self.reset()
        assert not self.data
        await self.subscribe(
            _wss_api, subscr_name=subscr_name, subscr_channel=subscr_channel
        )
        assert _wss_api._subscriptions == subscriptions
        assert self.data
        assert await _wss_api.unsubscribe(
            subscr_name=subscr_name, subscr_channel=subscr_channel
        )
        self.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "subscr_name, symbol, subscr_channel, subscriptions",
        [
            ("order_book", "btcusdt", "1", {"order_book": {"btcusdt": {"1"}}}),
            ("ORDER_BOOK", "BTCUSDT", "1", {"order_book": {"btcusdt": {"1"}}}),
            ("quote_bin", "btcusdt", "1", {"quote_bin": {"btcusdt": {"1"}}}),
            ("QUOTE_BIN", "BTCUSDT", "1", {"quote_bin": {"btcusdt": {"1"}}}),
            ("symbol", "btcusdt", "1", {"symbol": {"btcusdt": {"1"}}}),
            ("SYMBOL", "BTCUSDT", "1", {"symbol": {"btcusdt": {"1"}}}),
            ("trade", "btcusdt", "1", {"trade": {"btcusdt": {"1"}}}),
            ("TRADE", "BTCUSDT", "1", {"trade": {"btcusdt": {"1"}}}),
        ],
    )
    async def test_binance_wss_spot_subscribe_public_detail(
        self,
        _wss_api: BinanceWssApi,
        subscr_name,
        symbol,
        subscr_channel,
        subscriptions,
    ):
        self.reset()
        assert not self.data
        await self.subscribe(
            _wss_api,
            subscr_name=subscr_name,
            symbol=symbol,
            subscr_channel=subscr_channel,
        )
        assert _wss_api._subscriptions == subscriptions
        assert self.data
        symbol_message = None
        for obj in self.data:
            for data in obj[subscr_name.lower()]["data"]:
                if data["symbol"].lower() == symbol.lower():
                    symbol_message = obj
        assert symbol_message
        assert await _wss_api.unsubscribe(
            subscr_name=subscr_name, symbol=symbol, subscr_channel=subscr_channel
        )
        self.reset()

    def test_binance_wss_spot_is_unregistered(self, _testnet_wss_api: BinanceWssApi):
        _testnet_wss_api._subscriptions = {"symbol": {"btcusdt": {"1"}}}
        assert not _testnet_wss_api.is_unregistered(
            subscr_name="symbol", symbol="btcusdt"
        )
        assert not _testnet_wss_api.is_unregistered(
            subscr_name="SYMBOL", symbol="BTCUSDT"
        )
        assert _testnet_wss_api.is_unregistered(subscr_name="symbol")
        assert _testnet_wss_api.is_unregistered(subscr_name="symbol", symbol="ethusdt")
        assert _testnet_wss_api.is_unregistered(subscr_name="order")
        _testnet_wss_api._subscriptions = {"symbol": {"*": {"1"}}}
        assert not _testnet_wss_api.is_unregistered(subscr_name="symbol")
        assert _testnet_wss_api.is_unregistered(subscr_name="symbol", symbol="ethusdt")
        assert _testnet_wss_api.is_unregistered(subscr_name="order")

    def test_binance_wss_spot_unregister(self, _testnet_wss_api: BinanceWssApi):
        _testnet_wss_api._subscriptions = {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1", "2"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="symbol", symbol="xrpusdt", subscr_channel="1"
        ) == (False, "xrpusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1", "2"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="symbol", symbol="btcusdt", subscr_channel="3"
        ) == (False, "btcusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1", "2"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="order_book", symbol="btcusdt", subscr_channel="3"
        ) == (False, "btcusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1", "2"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="symbol", symbol="ethusdt", subscr_channel="2"
        ) == (False, "ethusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="symbol", symbol="ethusdt", subscr_channel="1"
        ) == (True, "ethusdt")
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}},
            "order": {"*": {"1", "2"}},
        }
        assert _testnet_wss_api.unregister(
            subscr_name="SYMBOL", symbol="BTCUSDT", subscr_channel="1"
        ) == (True, "btcusdt")
        assert _testnet_wss_api._subscriptions == {"order": {"*": {"1", "2"}}}
        assert _testnet_wss_api.unregister(subscr_name="order", subscr_channel="2") == (
            False,
            "*",
        )
        assert _testnet_wss_api._subscriptions == {"order": {"*": {"1"}}}
        assert _testnet_wss_api.unregister(subscr_name="order", subscr_channel="1") == (
            True,
            "*",
        )
        assert _testnet_wss_api._subscriptions == {}

    @pytest.mark.asyncio
    async def test_binance_wss_spot_unsubscribe(self, _testnet_wss_api: BinanceWssApi):
        _testnet_wss_api._subscriptions = {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1", "2"}},
            "order": {"*": {"1", "2"}},
        }
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="symbol", symbol="ethusdt", subscr_channel="2"
        )
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}, "ethusdt": {"1"}},
            "order": {"*": {"1", "2"}},
        }
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="SYMBOL", symbol="ETHUSDT", subscr_channel="1"
        )
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}},
            "order": {"*": {"1", "2"}},
        }
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="order_book", subscr_channel="1"
        )
        assert _testnet_wss_api._subscriptions == {
            "symbol": {"btcusdt": {"1"}},
            "order": {"*": {"1", "2"}},
        }
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="symbol", symbol="btcusdt", subscr_channel="1"
        )
        assert _testnet_wss_api._subscriptions == {"order": {"*": {"1", "2"}}}
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="order", subscr_channel="2"
        )
        assert _testnet_wss_api._subscriptions == {"order": {"*": {"1"}}}
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="order", subscr_channel="1"
        )
        assert _testnet_wss_api._subscriptions == {}
        assert _testnet_wss_api.handler is None
        assert _testnet_wss_api.tasks == []

    @pytest.mark.asyncio
    async def test_binance_wss_spot__restore_subscriptions(
        self, _testnet_wss_api: BinanceWssApi
    ):
        subscriptions = {"symbol": {"btcusdt": {"1"}}, "order": {"btcusdt": {"1"}}}
        _testnet_wss_api._subscriptions = subscriptions
        await _testnet_wss_api._restore_subscriptions()
        assert _testnet_wss_api._subscriptions == subscriptions
        _testnet_wss_api.auth_connect = False
        await _testnet_wss_api._restore_subscriptions()
        assert _testnet_wss_api._subscriptions == {"symbol": {"btcusdt": {"1"}}}
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="order", symbol="btcusdt", subscr_channel="1"
        )
        assert await _testnet_wss_api.unsubscribe(
            subscr_name="symbol", symbol="btcusdt", subscr_channel="1"
        )

    @pytest.mark.parametrize(
        "subscr_name, symbol",
        [("symbol", None), ("symbol", "btcusdt"), ("SYMBOL", "BTCUSDT")],
    )
    def test_binance_wss_spot_get_state(
        self, _testnet_wss_api: BinanceWssApi, subscr_name, symbol
    ):
        assert _testnet_wss_api.get_state(subscr_name, symbol) is None

    @pytest.mark.parametrize("symbol", [None, "not exists"])
    def test_binance_wss_spot_get_state_data_is_none(
        self, _testnet_wss_api: BinanceWssApi, symbol
    ):
        assert _testnet_wss_api.get_state_data(symbol) is None

    @pytest.mark.parametrize("symbol", ["btcusdt", "BTCUSDT"])
    def test_binance_wss_spot_get_state_data(
        self, _testnet_wss_api: BinanceWssApi, symbol
    ):
        assert (
            _testnet_wss_api.get_state_data(symbol)
            == STORAGE_DATA["symbol"][_testnet_wss_api.name][_testnet_wss_api.schema][
                symbol.lower()
            ]
        )

    @pytest.mark.parametrize(
        "message, result",
        [
            ({"result": None, "id": 1}, None),
            (json.dumps({"result": None, "id": 1}), {"result": None, "id": 1}),
            ("{result: None, id: 1}", {"raw": "{result: None, id: 1}"}),
        ],
    )
    def test_binance_wss_spot_parse_message(
        self, _testnet_wss_api: BinanceWssApi, message, result
    ):
        assert parse_message(message) == result

    @pytest.mark.parametrize(
        "message, result",
        [
            (SPOT_ORDER_MESSAGE, SPOT_ORDER_LOOKUP_TABLE_RESULT),
            (SPOT_ORDER_BOOK_MESSAGE, SPOT_ORDER_BOOK_LOOKUP_TABLE_RESULT),
            (SPOT_QUOTE_BIN_MESSAGE, SPOT_QUOTE_BIN_LOOKUP_TABLE_RESULT),
            (SPOT_SYMBOL_DETAIL_MESSAGE, SPOT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT),
            (SPOT_SYMBOL_MESSAGE, SPOT_SYMBOL_LOOKUP_TABLE_RESULT),
            (SPOT_TRADE_MESSAGE, SPOT_TRADE_LOOKUP_TABLE_RESULT),
            (SPOT_WALLET_MESSAGE, SPOT_WALLET_LOOKUP_TABLE_RESULT),
        ],
    )
    def test_binance_wss_spot__lookup_table(
        self, _testnet_wss_api: BinanceWssApi, message, result
    ):
        assert _testnet_wss_api._lookup_table(message) == result

    @pytest.mark.parametrize(
        "order_status, action",
        [
            (var.BINANCE_ORDER_STATUS_NEW, "insert"),
            (var.BINANCE_ORDER_DELETE_ACTION_STATUSES[0], "delete"),
            ("PARTIALLY_FILLED", "update"),
        ],
    )
    def test_binance_wss_spot_define_action_by_order_status(
        self, _testnet_wss_api: BinanceWssApi, order_status, action
    ):
        assert _testnet_wss_api.define_action_by_order_status(order_status) == action

    @pytest.mark.parametrize(
        "message, split_results",
        [
            (
                SPOT_ORDER_BOOK_LOOKUP_TABLE_RESULT,
                SPOT_ORDER_BOOK_SPLIT_MESSAGE_RESULTS,
            ),
            (SPOT_ORDER_LOOKUP_TABLE_RESULT, SPOT_ORDER_SPLIT_MESSAGE_RESULTS),
            (SPOT_QUOTE_BIN_LOOKUP_TABLE_RESULT, SPOT_QUOTE_BIN_SPLIT_MESSAGE_RESULTS),
            (
                SPOT_SYMBOL_DETAIL_LOOKUP_TABLE_RESULT,
                SPOT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULTS,
            ),
            (SPOT_SYMBOL_LOOKUP_TABLE_RESULT, SPOT_SYMBOL_SPLIT_MESSAGE_RESULTS),
            (SPOT_TRADE_LOOKUP_TABLE_RESULT, SPOT_TRADE_SPLIT_MESSAGE_RESULTS),
        ],
    )
    def test_binance_wss_spot__split_message(
        self, _testnet_wss_api: BinanceWssApi, message, split_results
    ):
        assert _testnet_wss_api._split_message(deepcopy(message)) == split_results

    def test_binance_wss_spot_split_wallet(self, _testnet_wss_api: BinanceWssApi):
        assert (
            _testnet_wss_api.split_wallet(deepcopy(SPOT_WALLET_LOOKUP_TABLE_RESULT))
            is None
        )
        _testnet_wss_api._subscriptions = {"wallet": {"btc": {"1"}}}
        assert (
            _testnet_wss_api.split_wallet(deepcopy(SPOT_WALLET_LOOKUP_TABLE_RESULT))
            == SPOT_WALLET_SPLIT_MESSAGE_RESULTS[0]
        )

    @pytest.mark.parametrize(
        "messages, results",
        [
            (SPOT_ORDER_BOOK_SPLIT_MESSAGE_RESULTS, SPOT_ORDER_BOOK_GET_DATA_RESULTS),
            (SPOT_ORDER_SPLIT_MESSAGE_RESULTS, SPOT_ORDER_GET_DATA_RESULTS),
            (SPOT_QUOTE_BIN_SPLIT_MESSAGE_RESULTS, SPOT_QUOTE_BIN_GET_DATA_RESULTS),
            (SPOT_TRADE_SPLIT_MESSAGE_RESULTS, SPOT_TRADE_GET_DATA_RESULTS),
            (SPOT_WALLET_SPLIT_MESSAGE_RESULTS, SPOT_WALLET_GET_DATA_RESULTS),
        ],
    )
    def test_binance_wss_spot_get_data(
        self, _testnet_wss_api: BinanceWssApi, messages, results
    ):
        for i, message in enumerate(messages):
            assert _testnet_wss_api.get_data(message) == results[i]

    @pytest.mark.parametrize(
        "messages, results",
        [
            (
                SPOT_SYMBOL_DETAIL_SPLIT_MESSAGE_RESULTS,
                SPOT_SYMBOL_DETAIL_GET_DATA_RESULTS,
            ),
            (SPOT_SYMBOL_SPLIT_MESSAGE_RESULTS, SPOT_SYMBOL_GET_DATA_RESULTS),
        ],
    )
    def test_binance_wss_spot_get_data_symbol(
        self, _testnet_wss_api: BinanceWssApi, messages, results
    ):
        for i, message in enumerate(messages):
            response = _testnet_wss_api.get_data(message)
            for j, data in enumerate(response["symbol"]["data"]):
                data["created"] = results[i]["symbol"]["data"][j]["created"]
            assert response == results[i]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message, results",
        [
            (SPOT_ORDER_MESSAGE, SPOT_ORDER_GET_DATA_RESULTS),
            (SPOT_ORDER_BOOK_MESSAGE, SPOT_ORDER_BOOK_GET_DATA_RESULTS),
            (SPOT_QUOTE_BIN_MESSAGE, SPOT_QUOTE_BIN_GET_DATA_RESULTS),
            (SPOT_TRADE_MESSAGE, SPOT_TRADE_GET_DATA_RESULTS),
        ],
    )
    async def test_binance_wss_spot_process_message(
        self, _testnet_wss_api: BinanceWssApi, message, results
    ):
        self.reset()
        assert not self.data
        await _testnet_wss_api.process_message(
            json.dumps(deepcopy(message)), self.on_message
        )
        assert self.data
        assert self.data == results
        self.reset()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message, results",
        [
            (SPOT_SYMBOL_DETAIL_MESSAGE, SPOT_SYMBOL_DETAIL_GET_DATA_RESULTS),
            (SPOT_SYMBOL_MESSAGE, SPOT_SYMBOL_GET_DATA_RESULTS),
        ],
    )
    async def test_binance_wss_spot_process_symbol_message(
        self, _testnet_wss_api: BinanceWssApi, message, results
    ):
        self.reset()
        assert not self.data
        await _testnet_wss_api.process_message(
            json.dumps(deepcopy(message)), self.on_message
        )
        assert self.data
        for i, message in enumerate(results):
            for j, obj in enumerate(message["symbol"]["data"]):
                self.data[i]["symbol"]["data"][j]["created"] = obj["created"]
        assert self.data == results
        self.reset()

    @pytest.mark.asyncio
    async def test_binance_wss_spot_process_wallet_message(
        self, _testnet_wss_api: BinanceWssApi
    ):
        self.reset()
        assert not self.data
        _testnet_wss_api._subscriptions = {"wallet": {"*": {"1"}}}
        await _testnet_wss_api.process_message(
            json.dumps(deepcopy(SPOT_WALLET_MESSAGE)), self.on_message
        )
        assert self.data == SPOT_PROCESS_WALLET_MESSAGE_RESULT
        self.reset()
