import json
import logging
import pytest
from copy import deepcopy
from mst_gateway.connector.api.stocks.binance import BinanceFuturesWssApi, var
from mst_gateway.connector.api.stocks.binance.wss import subscribers
from mst_gateway.connector.api.stocks.binance.wss.router import BinanceFuturesWssRouter
from mst_gateway.connector.api.utils import parse_message

from tests import config as cfg
from .data.storage import STORAGE_DATA

from .data.order import (
    FUTURES_ORDER_MESSAGE,
    FUTURES_ORDER_LOOKUP_TABLE_RESULT,
    FUTURES_ORDER_SPLIT_MESSAGE_RESULTS,
    FUTURES_ORDER_GET_DATA_RESULTS,
)
from .data.order_book import (
    FUTURES_ORDER_BOOK_MESSAGE,
    FUTURES_ORDER_BOOK_LOOKUP_TABLE_RESULT,
    FUTURES_ORDER_BOOK_SPLIT_MESSAGE_RESULTS,
    FUTURES_ORDER_BOOK_GET_DATA_RESULTS,
)
from .data.quote_bin import (
    FUTURES_QUOTE_BIN_MESSAGE,
    FUTURES_QUOTE_BIN_LOOKUP_TABLE_RESULT,
    FUTURES_QUOTE_BIN_SPLIT_MESSAGE_RESULTS,
    FUTURES_QUOTE_BIN_GET_DATA_RESULTS,
)
from .data.symbol import (
    FUTURES_SYMBOL_MESSAGE,
    FUTURES_SYMBOL_LOOKUP_TABLE_RESULT,
    FUTURES_SYMBOL_SPLIT_MESSAGE_RESULTS,
    FUTURES_SYMBOL_GET_DATA_RESULTS,
)
from .data.trade import (
    FUTURES_TRADE_MESSAGE,
    FUTURES_TRADE_LOOKUP_TABLE_RESULT,
    FUTURES_TRADE_SPLIT_MESSAGE_RESULTS,
    FUTURES_TRADE_GET_DATA_RESULTS,
)
from .data.wallet import (
    FUTURES_WALLET_MESSAGE,
    FUTURES_WALLET_LOOKUP_TABLE_RESULT,
    FUTURES_WALLET_SPLIT_MESSAGE_RESULTS,
    FUTURES_WALLET_GET_DATA_RESULTS,
    FUTURES_WALLET_PROCESS_MESSAGE_RESULTS,
)

logger = logging.getLogger(__name__)


@pytest.fixture
async def _wss_api() -> BinanceFuturesWssApi:
    with BinanceFuturesWssApi(
        url="wss://stream.binancefuture.com/ws",
        name=cfg.BINANCE_WSS_API_NAME,
        account_name=cfg.BINANCE_ACCOUNT_NAME,
        schema=cfg.BINANCE_FUTURES_SCHEMA,
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
async def _testnet_wss_api() -> BinanceFuturesWssApi:
    with BinanceFuturesWssApi(
        url=cfg.BINANCE_FUTURES_TESTNET_URL,
        name=cfg.BINANCE_WSS_API_NAME,
        account_name=cfg.BINANCE_ACCOUNT_NAME,
        schema=cfg.BINANCE_FUTURES_SCHEMA,
        auth=cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS,
        state_storage=deepcopy(STORAGE_DATA),
        logger=logger,
    ) as _testnet_wss_api:
        try:
            await _testnet_wss_api.open()
        except Exception as exc:
            logger.error(exc)
        yield _testnet_wss_api
        await _testnet_wss_api.close()


class TestBinanceFuturesWssApi:
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
                api_handler = await wss_api.open(is_auth=True, restore=True)

    async def subscribe(self, wss_api, subscr_channel, subscr_name, symbol=None):
        assert await wss_api.subscribe(subscr_channel, subscr_name, symbol)
        await self.consume(wss_api, wss_api.handler, self.on_message)

    def test_binance_wss_futures_str(self, _testnet_wss_api: BinanceFuturesWssApi):
        assert str(_testnet_wss_api) == cfg.BINANCE_WSS_API_NAME.lower()

    def test_binance_wss_futures_options(self, _testnet_wss_api: BinanceFuturesWssApi):
        assert _testnet_wss_api.options == {}

    def test_binance_wss_futures_subscriptions(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
        assert _testnet_wss_api.subscriptions == {}

    def test_binance_wss_futures_router(self, _testnet_wss_api: BinanceFuturesWssApi):
        assert isinstance(_testnet_wss_api.router, BinanceFuturesWssRouter)

    def test_binance_wss_futures_logger(self, _testnet_wss_api: BinanceFuturesWssApi):
        assert _testnet_wss_api.logger

    def test_binance_wss_futures_handler(self, _testnet_wss_api: BinanceFuturesWssApi):
        assert _testnet_wss_api.handler

    def test_binance_wss_futures_auth_data(
        self, _testnet_wss_api: BinanceFuturesWssApi, _wss_api: BinanceFuturesWssApi
    ):
        assert _testnet_wss_api.auth == cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS
        assert _wss_api.auth == cfg.BINANCE_AUTH_KEYS

    def test_binance_wss_futures_test(
        self, _testnet_wss_api: BinanceFuturesWssApi, _wss_api: BinanceFuturesWssApi
    ):
        assert _testnet_wss_api.test
        assert not _wss_api.test

    @pytest.mark.asyncio
    async def test_binance_wss_futures_open_auth(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
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
            ("symbol", subscribers.BinanceFuturesSymbolSubscriber),
            ("trade", subscribers.BinanceTradeSubscriber),
            ("wallet", subscribers.BinanceWalletSubscriber),
        ],
    )
    def test_binance_wss_futures__get_subscriber(
        self, _testnet_wss_api: BinanceFuturesWssApi, subscr_name, subscriber_class
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
    def test_binance_wss_futures_remap_subscriptions(
        self,
        _testnet_wss_api: BinanceFuturesWssApi,
        subscriptions,
        subscr_name,
        remap_result,
    ):
        _testnet_wss_api._subscriptions = subscriptions
        assert _testnet_wss_api.remap_subscriptions(subscr_name=subscr_name) is None
        assert _testnet_wss_api._subscriptions == remap_result

    def test_binance_wss_futures_is_registered(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
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

    def test_binance_wss_futures_register(self, _testnet_wss_api: BinanceFuturesWssApi):
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
    async def test_binance_wss_futures_subscribe_public(
        self,
        _wss_api: BinanceFuturesWssApi,
        subscr_name,
        subscr_channel,
        subscriptions,
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
    async def test_binance_wss_futures_subscribe_public_detail(
        self,
        _wss_api: BinanceFuturesWssApi,
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

    def test_binance_wss_futures_is_unregistered(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
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

    def test_binance_wss_futures_unregister(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
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
    async def test_binance_wss_futures_unsubscribe(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
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
    async def test_binance_wss_futures__restore_subscriptions(
        self, _testnet_wss_api: BinanceFuturesWssApi
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
    def test_binance_wss_futures_get_state(
        self, _testnet_wss_api: BinanceFuturesWssApi, subscr_name, symbol
    ):
        assert _testnet_wss_api.get_state(subscr_name, symbol) is None

    @pytest.mark.parametrize("symbol", [None, "not exists"])
    def test_binance_wss_futures_get_state_data_is_none(
        self, _testnet_wss_api: BinanceFuturesWssApi, symbol
    ):
        assert _testnet_wss_api.get_state_data(symbol) is None

    @pytest.mark.parametrize("symbol", ["btcusdt", "BTCUSDT"])
    def test_binance_wss_futures_get_state_data(
        self, _testnet_wss_api: BinanceFuturesWssApi, symbol
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
    def test_binance_wss_futures_parse_message(
        self, _testnet_wss_api: BinanceFuturesWssApi, message, result
    ):
        assert parse_message(message) == result

    @pytest.mark.parametrize(
        "message, result",
        [
            (FUTURES_ORDER_MESSAGE, FUTURES_ORDER_LOOKUP_TABLE_RESULT),
            (FUTURES_ORDER_BOOK_MESSAGE, FUTURES_ORDER_BOOK_LOOKUP_TABLE_RESULT),
            (FUTURES_QUOTE_BIN_MESSAGE, FUTURES_QUOTE_BIN_LOOKUP_TABLE_RESULT),
            (FUTURES_SYMBOL_MESSAGE, FUTURES_SYMBOL_LOOKUP_TABLE_RESULT),
            (FUTURES_TRADE_MESSAGE, FUTURES_TRADE_LOOKUP_TABLE_RESULT),
            (FUTURES_WALLET_MESSAGE, FUTURES_WALLET_LOOKUP_TABLE_RESULT),
        ],
    )
    def test_binance_wss_futures__lookup_table(
        self, _testnet_wss_api: BinanceFuturesWssApi, message, result
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
    def test_binance_wss_futures_define_action_by_order_status(
        self, _testnet_wss_api: BinanceFuturesWssApi, order_status, action
    ):
        assert _testnet_wss_api.define_action_by_order_status(order_status) == action

    @pytest.mark.parametrize(
        "message, split_results",
        [
            (FUTURES_ORDER_LOOKUP_TABLE_RESULT, FUTURES_ORDER_SPLIT_MESSAGE_RESULTS),
            (
                FUTURES_ORDER_BOOK_LOOKUP_TABLE_RESULT,
                FUTURES_ORDER_BOOK_SPLIT_MESSAGE_RESULTS,
            ),
            (
                FUTURES_QUOTE_BIN_LOOKUP_TABLE_RESULT,
                FUTURES_QUOTE_BIN_SPLIT_MESSAGE_RESULTS,
            ),
            (FUTURES_SYMBOL_LOOKUP_TABLE_RESULT, FUTURES_SYMBOL_SPLIT_MESSAGE_RESULTS),
            (FUTURES_TRADE_LOOKUP_TABLE_RESULT, FUTURES_TRADE_SPLIT_MESSAGE_RESULTS),
        ],
    )
    def test_binance_wss_futures__split_message(
        self, _testnet_wss_api: BinanceFuturesWssApi, message, split_results
    ):
        assert _testnet_wss_api._split_message(deepcopy(message)) == split_results

    def test_binance_wss_futures_split_wallet(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
        assert (
            _testnet_wss_api.split_wallet(deepcopy(FUTURES_WALLET_LOOKUP_TABLE_RESULT))
            is None
        )
        _testnet_wss_api._subscriptions = {"wallet": {"usdt": {"1"}}}
        assert (
            _testnet_wss_api.split_wallet(deepcopy(FUTURES_WALLET_LOOKUP_TABLE_RESULT))
            == FUTURES_WALLET_SPLIT_MESSAGE_RESULTS[0]
        )

    @pytest.mark.parametrize(
        "messages, results",
        [
            (
                FUTURES_ORDER_BOOK_SPLIT_MESSAGE_RESULTS,
                FUTURES_ORDER_BOOK_GET_DATA_RESULTS,
            ),
            (FUTURES_ORDER_SPLIT_MESSAGE_RESULTS, FUTURES_ORDER_GET_DATA_RESULTS),
            (
                FUTURES_QUOTE_BIN_SPLIT_MESSAGE_RESULTS,
                FUTURES_QUOTE_BIN_GET_DATA_RESULTS,
            ),
            (FUTURES_SYMBOL_SPLIT_MESSAGE_RESULTS, FUTURES_SYMBOL_GET_DATA_RESULTS),
            (FUTURES_TRADE_SPLIT_MESSAGE_RESULTS, FUTURES_TRADE_GET_DATA_RESULTS),
            (FUTURES_WALLET_SPLIT_MESSAGE_RESULTS, FUTURES_WALLET_GET_DATA_RESULTS),
        ],
    )
    def test_binance_wss_futures_get_data(
        self, _testnet_wss_api: BinanceFuturesWssApi, messages, results
    ):
        for i, message in enumerate(messages):
            assert _testnet_wss_api.get_data(message) == results[i]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message, results",
        [
            (FUTURES_ORDER_MESSAGE, FUTURES_ORDER_GET_DATA_RESULTS),
            (FUTURES_ORDER_BOOK_MESSAGE, FUTURES_ORDER_BOOK_GET_DATA_RESULTS),
            (FUTURES_QUOTE_BIN_MESSAGE, FUTURES_QUOTE_BIN_GET_DATA_RESULTS),
            (FUTURES_SYMBOL_MESSAGE, FUTURES_SYMBOL_GET_DATA_RESULTS),
            (FUTURES_TRADE_MESSAGE, FUTURES_TRADE_GET_DATA_RESULTS),
        ],
    )
    async def test_binance_wss_futures_process_message(
        self, _testnet_wss_api: BinanceFuturesWssApi, message, results
    ):
        self.reset()
        assert not self.data
        await _testnet_wss_api.process_message(
            json.dumps(deepcopy(message)), self.on_message
        )
        assert self.data == results
        self.reset()

    @pytest.mark.asyncio
    async def test_binance_wss_futures_process_wallet_message(
        self, _testnet_wss_api: BinanceFuturesWssApi
    ):
        self.reset()
        assert not self.data
        _testnet_wss_api._subscriptions = {"wallet": {"*": {"1"}}}
        await _testnet_wss_api.process_message(
            json.dumps(deepcopy(FUTURES_WALLET_MESSAGE)), self.on_message
        )
        assert self.data == FUTURES_WALLET_PROCESS_MESSAGE_RESULTS
        self.reset()
