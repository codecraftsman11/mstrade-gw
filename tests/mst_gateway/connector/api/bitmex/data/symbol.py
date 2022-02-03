from mst_gateway.connector.api import OrderSchema

DEFAULT_SYMBOL_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"instrument","action":"partial","data":[{"symbol":"XBTUSD","rootSymbol":"XBT","state":"Open","typ":"FFWCSX","listing":"2016-05-04T12:00:00.000Z","front":"2016-05-04T12:00:00.000Z","expiry":null,"settle":null,"listedSettle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"USD","underlying":"XBT","quoteCurrency":"USD","underlyingSymbol":"XBT=","reference":"BMEX","referenceSymbol":".BXBT","calcInterval":null,"publishInterval":null,"publishTime":null,"maxOrderQty":10000000,"maxPrice":1000000,"lotSize":100,"tickSize":0.5,"multiplier":-100000000,"settlCurrency":"XBt","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":-100000000,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":true,"initMargin":0.01,"maintMargin":0.0035,"riskLimit":20000000000,"riskStep":15000000000,"limit":null,"capped":false,"taxed":true,"deleverage":true,"makerFee":-0.0001,"takerFee":0.0005,"settlementFee":0,"insuranceFee":0,"fundingBaseSymbol":".XBTBON8H","fundingQuoteSymbol":".USDBON8H","fundingPremiumSymbol":".XBTUSDPI8H","fundingTimestamp":"2021-12-18T20:00:00.000Z","fundingInterval":"2000-01-01T08:00:00.000Z","fundingRate":0.0001,"indicativeFundingRate":0.0001,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":"2021-12-18T19:00:00.000Z","closingTimestamp":"2021-12-18T20:00:00.000Z","sessionInterval":"2000-01-01T01:00:00.000Z","prevClosePrice":47090.75,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":146867056930,"totalVolume":146867106330,"volume":49400,"volume24h":3513000,"prevTotalTurnover":1952473742211136,"totalTurnover":1952473848244273,"turnover":106033137,"turnover24h":7576400767,"homeNotional24h":75.76400767000001,"foreignNotional24h":3513000,"prevPrice24h":46804.5,"vwap":46367.78,"highPrice":47251,"lowPrice":45619.5,"lastPrice":46672,"lastPriceProtected":46672,"lastTickDirection":"ZeroPlusTick","lastChangePcnt":-0.0028,"bidPrice":46671.5,"midPrice":46671.75,"askPrice":46672,"impactBidPrice":46661.8138,"impactMidPrice":46720.5,"impactAskPrice":46779.0299,"hasLiquidity":true,"openInterest":66341700,"openValue":142046867538,"fairMethod":"FundingRate","fairBasisRate":0.1095,"fairBasis":0.05,"fairPrice":46704.01,"markMethod":"FairPrice","markPrice":46704.01,"indicativeTaxRate":0,"indicativeSettlePrice":46703.96,"optionUnderlyingPrice":null,"settledPriceAdjustmentRate":null,"settledPrice":null,"timestamp":"2021-12-18T19:55:00.000Z"}]}',
            'expect': {
                "symbol": {
                    "acc": "tbitmex",
                    "tb": "symbol",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "tm": "2021-12-18T19:55:00.000000",
                            "s": "XBTUSD",
                            "p": 46672.0,
                            "p24": 46804.5,
                            "dt": -0.28,
                            "fp": 2.1426122728830992e-05,
                            "bip": 46671.5,
                            "asp": 46672.0,
                            "re": True,
                            "v24": 3513000,
                            "mp": 46704.01,
                            "hip": 47251.0,
                            "lop": 45619.5,
                            "exp": None,
                            "expd": None,
                            "pa": ["XBT", "USD"],
                            "tck": 0.5,
                            "vt": 100.0,
                            "ss": "btcusd",
                            "crt": "2020-07-01T15:10:16.748936",
                            "mlvr": 100.0,
                        }
                    ],
                }
            }

        },
        {
            'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","lastPrice":46691.5,"timestamp":"2021-12-18T20:03:16.369Z","lastChangePcnt":-0.0022}]}',
            'expect': {
                "symbol": {
                    "acc": "tbitmex",
                    "tb": "symbol",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-18T20:03:16.369000",
                            "s": "XBTUSD",
                            "p": 46691.5,
                            "p24": 46804.5,
                            "dt": -0.24,
                            "fp": 2.1417174432177163e-05,
                            "bip": 46671.5,
                            "asp": 46672.0,
                            "re": True,
                            "v24": 3513000,
                            "mp": 46704.01,
                            "hip": 47251.0,
                            "lop": 45619.5,
                            "exp": None,
                            "expd": None,
                            "pa": ["XBT", "USD"],
                            "tck": 0.5,
                            "vt": 100.0,
                            "ss": "btcusd",
                            "crt": "2020-07-01T15:10:16.748936",
                            "mlvr": 100.0,
                        }
                    ],
                }
            },
        },
        {
            'message': '{"table":"instrument","action":"update","data":[{"symbol":"XBTUSD","fairPrice":46599.19,"fairBasis":4.63,"lastPriceProtected":46683,"markPrice":46599.19,"openValue":142366634532,"timestamp":"2021-12-18T20:03:05.000Z","indicativeSettlePrice":46594.56}]}',
            'expect': {
                "symbol": {
                    "acc": "tbitmex",
                    "tb": "symbol",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-18T20:03:05.000000",
                            "s": "XBTUSD",
                            "p": 46691.5,
                            "p24": 46804.5,
                            "dt": -0.24,
                            "fp": 2.1417174432177163e-05,
                            "bip": 46671.5,
                            "asp": 46672.0,
                            "re": True,
                            "v24": 3513000,
                            "mp": 46599.19,
                            "hip": 47251.0,
                            "lop": 45619.5,
                            "exp": None,
                            "expd": None,
                            "pa": ["XBT", "USD"],
                            "tck": 0.5,
                            "vt": 100.0,
                            "ss": "btcusd",
                            "crt": "2020-07-01T15:10:16.748936",
                            "mlvr": 100.0,
                        }
                    ],
                }
            }

        }
    ]
}

