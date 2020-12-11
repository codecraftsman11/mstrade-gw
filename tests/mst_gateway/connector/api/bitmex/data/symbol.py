from mst_gateway.connector.api.stocks.bitmex.utils import to_iso_datetime
import tests.config as cfg


TEST_SYMBOL_MESSAGES = [
    {
        'message': '{"table":"instrument","action":"partial","keys":["symbol"],"types":{"symbol":"symbol","rootSymbol":"symbol","state":"symbol","typ":"symbol","listing":"timestamp","front":"timestamp","expiry":"timestamp","settle":"timestamp","relistInterval":"timespan","inverseLeg":"symbol","sellLeg":"symbol","buyLeg":"symbol","optionStrikePcnt":"float","optionStrikeRound":"float","optionStrikePrice":"float","optionMultiplier":"float","positionCurrency":"symbol","underlying":"symbol","quoteCurrency":"symbol","underlyingSymbol":"symbol","reference":"symbol","referenceSymbol":"symbol","calcInterval":"timespan","publishInterval":"timespan","publishTime":"timespan","maxOrderQty":"long","maxPrice":"float","lotSize":"long","tickSize":"float","multiplier":"long","settlCurrency":"symbol","underlyingToPositionMultiplier":"long","underlyingToSettleMultiplier":"long","quoteToSettleMultiplier":"long","isQuanto":"boolean","isInverse":"boolean","initMargin":"float","maintMargin":"float","riskLimit":"long","riskStep":"long","limit":"float","capped":"boolean","taxed":"boolean","deleverage":"boolean","makerFee":"float","takerFee":"float","settlementFee":"float","insuranceFee":"float","fundingBaseSymbol":"symbol","fundingQuoteSymbol":"symbol","fundingPremiumSymbol":"symbol","fundingTimestamp":"timestamp","fundingInterval":"timespan","fundingRate":"float","indicativeFundingRate":"float","rebalanceTimestamp":"timestamp","rebalanceInterval":"timespan","openingTimestamp":"timestamp","closingTimestamp":"timestamp","sessionInterval":"timespan","prevClosePrice":"float","limitDownPrice":"float","limitUpPrice":"float","bankruptLimitDownPrice":"float","bankruptLimitUpPrice":"float","prevTotalVolume":"long","totalVolume":"long","volume":"long","volume24h":"long","prevTotalTurnover":"long","totalTurnover":"long","turnover":"long","turnover24h":"long","homeNotional24h":"float","foreignNotional24h":"float","prevPrice24h":"float","vwap":"float","highPrice":"float","lowPrice":"float","lastPrice":"float","lastPriceProtected":"float","lastTickDirection":"symbol","lastChangePcnt":"float","bidPrice":"float","midPrice":"float","askPrice":"float","impactBidPrice":"float","impactMidPrice":"float","impactAskPrice":"float","hasLiquidity":"boolean","openInterest":"long","openValue":"long","fairMethod":"symbol","fairBasisRate":"float","fairBasis":"float","fairPrice":"float","markMethod":"symbol","markPrice":"float","indicativeTaxRate":"float","indicativeSettlePrice":"float","optionUnderlyingPrice":"float","settledPrice":"float","timestamp":"timestamp"},"foreignKeys":{"inverseLeg":"instrument","sellLeg":"instrument","buyLeg":"instrument"},"attributes":{"symbol":"unique"},"filter":{"symbol":"XBTUSD"},"data":[{"symbol":"XBTUSD","rootSymbol":"XBT","state":"Open","typ":"FFWCSX","listing":"2016-05-13T12:00:00.000Z","front":"2016-05-13T12:00:00.000Z","expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"USD","underlying":"XBT","quoteCurrency":"USD","underlyingSymbol":"XBT=","reference":"BMEX","referenceSymbol":".BXBT","calcInterval":null,"publishInterval":null,"publishTime":null,"maxOrderQty":10000000,"maxPrice":1000000,"lotSize":1,"tickSize":0.5,"multiplier":-100000000,"settlCurrency":"XBt","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":-100000000,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":true,"initMargin":0.01,"maintMargin":0.004,"riskLimit":20000000000,"riskStep":10000000000,"limit":null,"capped":false,"taxed":true,"deleverage":true,"makerFee":-0.00025,"takerFee":0.00075,"settlementFee":0,"insuranceFee":0,"fundingBaseSymbol":".XBTBON8H","fundingQuoteSymbol":".USDBON8H","fundingPremiumSymbol":".XBTUSDPI8H","fundingTimestamp":"2020-07-22T12:00:00.000Z","fundingInterval":"2000-01-01T08:00:00.000Z","fundingRate":0.0001,"indicativeFundingRate":0.0001,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":"2020-07-22T10:00:00.000Z","closingTimestamp":"2020-07-22T11:00:00.000Z","sessionInterval":"2000-01-01T01:00:00.000Z","prevClosePrice":9352.38,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":2369794442422,"totalVolume":2369808707968,"volume":14265546,"volume24h":997235816,"prevTotalTurnover":32520340578382656,"totalTurnover":32520493503356430,"turnover":152924973776,"turnover24h":10644181384570,"homeNotional24h":106441.81384569843,"foreignNotional24h":997235816,"prevPrice24h":9351,"vwap":9369.4369,"highPrice":9447,"lowPrice":9290,"lastPrice":9339,"lastPriceProtected":9339,"lastTickDirection":"ZeroMinusTick","lastChangePcnt":-0.0013,"bidPrice":9339,"midPrice":9339.25,"askPrice":9339.5,"impactBidPrice":9338.8121,"impactMidPrice":9339.25,"impactAskPrice":9339.6843,"hasLiquidity":true,"openInterest":737748536,"openValue":7897598077880,"fairMethod":"FundingRate","fairBasisRate":0.1095,"fairBasis":0.14,"fairPrice":9341.21,"markMethod":"FairPrice","markPrice":9341.21,"indicativeTaxRate":0,"indicativeSettlePrice":9341.07,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2020-07-22T10:50:00.794000Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "partial",
            'data': [
                {
                    "time": to_iso_datetime("2020-07-22T10:50:00.794000Z"),
                    "timestamp": 1595415000794,
                    "symbol": "XBTUSD",
                    "price": 9339.0,
                    "price24": 9351.0,
                    "delta": -0.13,
                    "face_price": 0.00010707784559374665,
                    "bid_price": 9339.0,
                    "ask_price": 9339.5,
                    "reversed": True,
                    "volume24": 997235816,
                    "pair": [
                        "XBT",
                        "USD"
                    ],
                    "tick": 0.5,
                    "system_symbol": "btcusd",
                    "schema": "margin1",
                    "symbol_schema": "margin1",
                    "expiration": None,
                    "created": to_iso_datetime("2020-06-25T13:03:00.295118Z"),
                }
            ]
        }
    },
    {
        'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","lastPriceProtected":9342,"fairPrice":9341.13,"markPrice":9341.13,"indicativeSettlePrice":9340.99,"timestamp":"2020-07-22T10:50:00.794000Z"}]}',
        'data': None
    },
    {
        'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","lastPrice":9339,"timestamp":"2020-07-22T10:50:00.794000Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "update",
            'data': [
                {
                    "time": to_iso_datetime("2020-07-22T10:50:00.794000Z"),
                    "timestamp": 1595415000794,
                    "symbol": "XBTUSD",
                    "price": 9339.0,
                    "price24": 9351.0,
                    "delta": -0.13,
                    "face_price": 0.00010707784559374665,
                    "bid_price": 9339.0,
                    "ask_price": 9339.5,
                    "reversed": True,
                    "volume24": 997235816,
                    "pair": [
                        "XBT",
                        "USD"
                    ],
                    "tick": 0.5,
                    "system_symbol": "btcusd",
                    "schema": "margin1",
                    "symbol_schema": "margin1",
                    "expiration": None,
                    "created": to_iso_datetime("2020-06-25T13:03:00.295118Z"),
                }
            ]
        }
    },
]

RESULT_SYMBOL_STATE = {
    'account': "bitmex.test",
    'table': "symbol",
    'schema': cfg.BITMEX_SCHEMA,
    'action': "partial",
    'data': [
        {
            "time": to_iso_datetime("2020-07-22T10:50:00.794000Z"),
            "timestamp": 1595415000794,
            "symbol": "XBTUSD",
            "price": 9339.0,
            "price24": 9351.0,
            "delta": -0.13,
            "face_price": 0.00010707784559374665,
            "bid_price": 9339.0,
            "ask_price": 9339.5,
            "reversed": True,
            "volume24": 997235816,
            "pair": [
                "XBT",
                "USD"
            ],
            "tick": 0.5,
            "system_symbol": "btcusd",
            "schema": "margin1",
            "symbol_schema": "margin1",
            "expiration": None,
            "created": to_iso_datetime("2020-06-25T13:03:00.295118Z"),
        }
    ]
}
