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

TEST_SYMBOL_MESSAGES = [
    {
        'message':
        '{"table":"instrument","action":"partial","data":[{"symbol":"XBTUSD","rootSymbol":"XBT","state":"Open","typ":"FFWCSX","listing":"2016-05-04T12:00:00.000Z","front":"2016-05-04T12:00:00.000Z","expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"USD","underlying":"XBT","quoteCurrency":"USD","underlyingSymbol":"XBT=","reference":"BMEX","referenceSymbol":".BXBT","calcInterval":null,"publishInterval":null,"publishTime":null,"maxOrderQty":10000000,"maxPrice":1000000,"lotSize":1,"tickSize":0.5,"multiplier":-100000000,"settlCurrency":"XBt","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":-100000000,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":true,"initMargin":0.01,"maintMargin":0.005,"riskLimit":20000000000,"riskStep":10000000000,"limit":null,"capped":false,"taxed":true,"deleverage":true,"makerFee":-0.00025,"takerFee":0.00075,"settlementFee":0,"insuranceFee":0,"fundingBaseSymbol":".XBTBON8H","fundingQuoteSymbol":".USDBON8H","fundingPremiumSymbol":".XBTUSDPI8H","fundingTimestamp":"2019-07-15T20:00:00.000Z","fundingInterval":"2000-01-01T08:00:00.000Z","fundingRate":0.00375,"indicativeFundingRate":0.00375,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":"2019-07-15T14:00:00.000Z","closingTimestamp":"2019-07-15T15:00:00.000Z","sessionInterval":"2000-01-01T01:00:00.000Z","prevClosePrice":10310.8,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":111636013823,"totalVolume":111641355252,"volume":5341429,"volume24h":108869364,"prevTotalTurnover":1646941080067345,"totalTurnover":1646991571069248,"turnover":50491001903,"turnover24h":1032334982775,"homeNotional24h":10323.349827749991,"foreignNotional24h":108869364,"prevPrice24h":10864,"vwap":10546.2982,"highPrice":11000,"lowPrice":10200,"lastPrice":10650,"lastPriceProtected":10650,"lastTickDirection":"PlusTick","lastChangePcnt":-0.0197,"bidPrice":10649.5,"midPrice":10649.75,"askPrice":10650,"impactBidPrice":10636.0349,"impactMidPrice":10656,"impactAskPrice":10675.7767,"hasLiquidity":true,"openInterest":113766442,"openValue":1078278337276,"fairMethod":"FundingRate","fairBasisRate":4.10625,"fairBasis":25.74,"fairPrice":10551.29,"markMethod":"FairPrice","markPrice":10551.29,"indicativeTaxRate":0,"indicativeSettlePrice":10525.55,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-15T14:47:10.000Z"},{"symbol":".EVOL7D","rootSymbol":"EVOL","state":"Unlisted","typ":"MRIXXX","listing":null,"front":null,"expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"","underlying":"ETH","quoteCurrency":"XXX","underlyingSymbol":".EVOL7D","reference":"BMEX","referenceSymbol":".BETHXBT","calcInterval":"2000-01-08T00:00:00.000Z","publishInterval":"2000-01-01T00:05:00.000Z","publishTime":null,"maxOrderQty":null,"maxPrice":null,"lotSize":null,"tickSize":0.01,"multiplier":null,"settlCurrency":"","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":null,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":false,"initMargin":null,"maintMargin":null,"riskLimit":null,"riskStep":null,"limit":null,"capped":false,"taxed":false,"deleverage":false,"makerFee":null,"takerFee":null,"settlementFee":null,"insuranceFee":null,"fundingBaseSymbol":"","fundingQuoteSymbol":"","fundingPremiumSymbol":"","fundingTimestamp":null,"fundingInterval":null,"fundingRate":null,"indicativeFundingRate":null,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":null,"closingTimestamp":null,"sessionInterval":null,"prevClosePrice":null,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":null,"totalVolume":null,"volume":null,"volume24h":null,"prevTotalTurnover":null,"totalTurnover":null,"turnover":null,"turnover24h":null,"homeNotional24h":null,"foreignNotional24h":null,"prevPrice24h":10.86,"vwap":null,"highPrice":null,"lowPrice":null,"lastPrice":10.79,"lastPriceProtected":null,"lastTickDirection":"ZeroMinusTick","lastChangePcnt":-0.0064,"bidPrice":null,"midPrice":null,"askPrice":null,"impactBidPrice":null,"impactMidPrice":null,"impactAskPrice":null,"hasLiquidity":false,"openInterest":null,"openValue":0,"fairMethod":"","fairBasisRate":null,"fairBasis":null,"fairPrice":null,"markMethod":"LastPrice","markPrice":10.79,"indicativeTaxRate":null,"indicativeSettlePrice":null,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-18T20:35:00.000Z"},{"symbol":"XBTEUR","rootSymbol":"EVOL","state":"Open","typ":"MRIXXX","listing":null,"front":null,"expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"","underlying":"ETH","quoteCurrency":"XXX","underlyingSymbol":".EVOL7D","reference":"BMEX","referenceSymbol":".BETHXBT","calcInterval":"2000-01-08T00:00:00.000Z","publishInterval":"2000-01-01T00:05:00.000Z","publishTime":null,"maxOrderQty":null,"maxPrice":null,"lotSize":null,"tickSize":0.01,"multiplier":null,"settlCurrency":"","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":null,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":false,"initMargin":null,"maintMargin":null,"riskLimit":null,"riskStep":null,"limit":null,"capped":false,"taxed":false,"deleverage":false,"makerFee":null,"takerFee":null,"settlementFee":null,"insuranceFee":null,"fundingBaseSymbol":"","fundingQuoteSymbol":"","fundingPremiumSymbol":"","fundingTimestamp":null,"fundingInterval":null,"fundingRate":null,"indicativeFundingRate":null,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":null,"closingTimestamp":null,"sessionInterval":null,"prevClosePrice":null,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":null,"totalVolume":null,"volume":null,"volume24h":null,"prevTotalTurnover":null,"totalTurnover":null,"turnover":null,"turnover24h":null,"homeNotional24h":null,"foreignNotional24h":null,"prevPrice24h":10.86,"vwap":null,"highPrice":null,"lowPrice":null,"lastPrice":10.79,"lastPriceProtected":null,"lastTickDirection":"ZeroMinusTick","lastChangePcnt":-0.0064,"bidPrice":null,"midPrice":null,"askPrice":null,"impactBidPrice":null,"impactMidPrice":null,"impactAskPrice":null,"hasLiquidity":false,"openInterest":null,"openValue":0,"fairMethod":"","fairBasisRate":null,"fairBasis":null,"fairPrice":null,"markMethod":"LastPrice","markPrice":10.79,"indicativeTaxRate":null,"indicativeSettlePrice":null,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-18T20:35:00.000Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'type': "partial",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'timestamp': _date("2019-07-15T14:47:10.000Z"),
                    'price': 10650
                },
                {
                    'symbol': "XBTEUR",
                    'timestamp': _date("2019-07-18T20:35:00.000Z"),
                    'price': 10.79
                }
            ]
        }
    },
    {
        'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","fairPrice":10933.67,"markPrice":10933.67,"timestamp":"2019-07-01T08:16:15.250Z"}]}',
        'data': None
    },
    {
        'message':
        '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","lastPrice":10933.67,"markPrice":10933.67,"timestamp":"2019-07-01T08:16:15.250Z"},{"symbol":".EVOL7D","lastPrice":10933.67,"markPrice":10933.67,"timestamp":"2019-07-01T08:16:15.250Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'type': "update",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'timestamp': _date("2019-07-01T08:16:15.250Z"),
                    'price': 10933.67
                }
            ]
        }
    },
]

TEST_QUOTE_BIN_MESSAGES = [
    {
        'message': '{"table": "trade", "action": "invalid"}',
        'data': None,
        'data_trade': None
    },
    {
        'message': '{"table":"trade","action":"partial","data":[{"timestamp":"2019-07-01T10:29:04.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': None,
        'data_trade': None
    },
    {
        'message': '{"table":"tradeBin1m","action":"partial","data":[{"timestamp":"2019-07-01T10:30:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "partial",
            'data': [
                {
                    'timestamp': _date("2019-07-01T10:30:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "partial",
            'data': [
                {
                    'timestamp': _date("2019-07-01T10:30:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        },
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:58:09.589Z","symbol":"XBTUSD","side":"Buy","size":10,"price":11397.5,"tickDirection":"ZeroPlusTick","trdMatchID":"c05d0c8d-d4fc-97d1-ff13-7f36213f5240","grossValue":87740,"homeNotional":0.0008774,"foreignNotional":10}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:58:09.589Z"),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:58:09.589Z"),
                    'symbol': "XBTUSD",
                    'volume': 10,
                    'open': 11397.5,
                    'close': 11397.5,
                    'low': 11397.5,
                    'high': 11397.5,
                }
            ]
        },
    },
    {
        'message': '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2019-07-01T11:59:00.000Z","symbol":"XBTUSD","open":11322.5,"high":11331,"low":11319.5,"close":11321,"trades":66,"volume":7187,"vwap":11326.311,"lastSize":5,"turnover":63458685,"homeNotional":0.6345868499999999,"foreignNotional":7187}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:59:00.000Z"),
                    'symbol': "XBTUSD",
                    'volume': 7187,
                    'open': 11322.5,
                    'close': 11321,
                    'low': 11319.5,
                    'high': 11331,
                }
            ]
        },
        'data_trade': None
    },
    {
        'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2019-07-01T11:59:36.307Z","symbol":"XBTUSD","side":"Sell","size":100,"price":11329,"tickDirection":"MinusTick","trdMatchID":"4e2522dc-c411-46dc-7f2f-e33491965ddd","grossValue":882700,"homeNotional":0.008827,"foreignNotional":100}]}',
        'data': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:59:36.307Z"),
                    'symbol': "XBTUSD",
                    'volume': 100,
                    'open': 11329,
                    'close': 11329,
                    'low': 11329,
                    'high': 11329
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
            'data': [
                {
                    'timestamp': _date("2019-07-01T11:59:36.307Z"),
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
                    'timestamp': _date("2019-07-01T11:59:38.326Z"),
                    'symbol': "XBTUSD",
                    'volume': 105,
                    'open': 11329,
                    'close': 11339,
                    'low': 11329,
                    'high': 11339
                }
            ]
        },
        'data_trade': {
            'account': "bitmex.test",
            'table': "quote_bin",
            'type': "update",
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
            'type': "partial",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'timestamp': _date("2019-07-01T08:16:15.250Z"),
                    'price': 10933.67
                },
                {
                    'symbol': "XBTEUR",
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
            'type': "partial",
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
