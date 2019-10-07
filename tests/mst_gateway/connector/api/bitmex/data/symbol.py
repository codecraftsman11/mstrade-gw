from mst_gateway.connector.api.stocks.bitmex.utils import _date


TEST_SYMBOL_MESSAGES = [
    {
        'message':
        '{"table":"instrument","action":"partial","data":[{"symbol":"XBTUSD","rootSymbol":"XBT","state":"Open","typ":"FFWCSX","listing":"2016-05-04T12:00:00.000Z","front":"2016-05-04T12:00:00.000Z","expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"USD","underlying":"XBT","quoteCurrency":"USD","underlyingSymbol":"XBT=","reference":"BMEX","referenceSymbol":".BXBT","calcInterval":null,"publishInterval":null,"publishTime":null,"maxOrderQty":10000000,"maxPrice":1000000,"lotSize":1,"tickSize":0.5,"multiplier":-100000000,"settlCurrency":"XBt","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":-100000000,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":true,"initMargin":0.01,"maintMargin":0.005,"riskLimit":20000000000,"riskStep":10000000000,"limit":null,"capped":false,"taxed":true,"deleverage":true,"makerFee":-0.00025,"takerFee":0.00075,"settlementFee":0,"insuranceFee":0,"fundingBaseSymbol":".XBTBON8H","fundingQuoteSymbol":".USDBON8H","fundingPremiumSymbol":".XBTUSDPI8H","fundingTimestamp":"2019-07-15T20:00:00.000Z","fundingInterval":"2000-01-01T08:00:00.000Z","fundingRate":0.00375,"indicativeFundingRate":0.00375,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":"2019-07-15T14:00:00.000Z","closingTimestamp":"2019-07-15T15:00:00.000Z","sessionInterval":"2000-01-01T01:00:00.000Z","prevClosePrice":10310.8,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":111636013823,"totalVolume":111641355252,"volume":5341429,"volume24h":108869364,"prevTotalTurnover":1646941080067345,"totalTurnover":1646991571069248,"turnover":50491001903,"turnover24h":1032334982775,"homeNotional24h":10323.349827749991,"foreignNotional24h":108869364,"prevPrice24h":10864,"vwap":10546.2982,"highPrice":11000,"lowPrice":10200,"lastPrice":10650,"lastPriceProtected":10650,"lastTickDirection":"PlusTick","lastChangePcnt":-0.0197,"bidPrice":10649.5,"midPrice":10649.75,"askPrice":10650,"impactBidPrice":10636.0349,"impactMidPrice":10656,"impactAskPrice":10675.7767,"hasLiquidity":true,"openInterest":113766442,"openValue":1078278337276,"fairMethod":"FundingRate","fairBasisRate":4.10625,"fairBasis":25.74,"fairPrice":10551.29,"markMethod":"FairPrice","markPrice":10551.29,"indicativeTaxRate":0,"indicativeSettlePrice":10525.55,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-15T14:47:10.000Z"},{"symbol":".EVOL7D","rootSymbol":"EVOL","state":"Unlisted","typ":"MRIXXX","listing":null,"front":null,"expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"","underlying":"ETH","quoteCurrency":"XXX","underlyingSymbol":".EVOL7D","reference":"BMEX","referenceSymbol":".BETHXBT","calcInterval":"2000-01-08T00:00:00.000Z","publishInterval":"2000-01-01T00:05:00.000Z","publishTime":null,"maxOrderQty":null,"maxPrice":null,"lotSize":null,"tickSize":0.01,"multiplier":null,"settlCurrency":"","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":null,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":false,"initMargin":null,"maintMargin":null,"riskLimit":null,"riskStep":null,"limit":null,"capped":false,"taxed":false,"deleverage":false,"makerFee":null,"takerFee":null,"settlementFee":null,"insuranceFee":null,"fundingBaseSymbol":"","fundingQuoteSymbol":"","fundingPremiumSymbol":"","fundingTimestamp":null,"fundingInterval":null,"fundingRate":null,"indicativeFundingRate":null,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":null,"closingTimestamp":null,"sessionInterval":null,"prevClosePrice":null,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":null,"totalVolume":null,"volume":null,"volume24h":null,"prevTotalTurnover":null,"totalTurnover":null,"turnover":null,"turnover24h":null,"homeNotional24h":null,"foreignNotional24h":null,"prevPrice24h":10.86,"vwap":null,"highPrice":null,"lowPrice":null,"lastPrice":10.79,"lastPriceProtected":null,"lastTickDirection":"ZeroMinusTick","lastChangePcnt":-0.0064,"bidPrice":null,"midPrice":null,"askPrice":null,"impactBidPrice":null,"impactMidPrice":null,"impactAskPrice":null,"hasLiquidity":false,"openInterest":null,"openValue":0,"fairMethod":"","fairBasisRate":null,"fairBasis":null,"fairPrice":null,"markMethod":"LastPrice","markPrice":10.79,"indicativeTaxRate":null,"indicativeSettlePrice":null,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-18T20:35:00.000Z"},{"symbol":"XBTEUR","rootSymbol":"EVOL","state":"Open","typ":"MRIXXX","listing":null,"front":null,"expiry":null,"settle":null,"relistInterval":null,"inverseLeg":"","sellLeg":"","buyLeg":"","optionStrikePcnt":null,"optionStrikeRound":null,"optionStrikePrice":null,"optionMultiplier":null,"positionCurrency":"","underlying":"ETH","quoteCurrency":"XXX","underlyingSymbol":".EVOL7D","reference":"BMEX","referenceSymbol":".BETHXBT","calcInterval":"2000-01-08T00:00:00.000Z","publishInterval":"2000-01-01T00:05:00.000Z","publishTime":null,"maxOrderQty":null,"maxPrice":null,"lotSize":null,"tickSize":0.01,"multiplier":null,"settlCurrency":"","underlyingToPositionMultiplier":null,"underlyingToSettleMultiplier":null,"quoteToSettleMultiplier":null,"isQuanto":false,"isInverse":false,"initMargin":null,"maintMargin":null,"riskLimit":null,"riskStep":null,"limit":null,"capped":false,"taxed":false,"deleverage":false,"makerFee":null,"takerFee":null,"settlementFee":null,"insuranceFee":null,"fundingBaseSymbol":"","fundingQuoteSymbol":"","fundingPremiumSymbol":"","fundingTimestamp":null,"fundingInterval":null,"fundingRate":null,"indicativeFundingRate":null,"rebalanceTimestamp":null,"rebalanceInterval":null,"openingTimestamp":null,"closingTimestamp":null,"sessionInterval":null,"prevClosePrice":null,"limitDownPrice":null,"limitUpPrice":null,"bankruptLimitDownPrice":null,"bankruptLimitUpPrice":null,"prevTotalVolume":null,"totalVolume":null,"volume":null,"volume24h":null,"prevTotalTurnover":null,"totalTurnover":null,"turnover":null,"turnover24h":null,"homeNotional24h":null,"foreignNotional24h":null,"prevPrice24h":10.86,"vwap":null,"highPrice":null,"lowPrice":null,"lastPrice":10.79,"lastPriceProtected":null,"lastTickDirection":"ZeroMinusTick","lastChangePcnt":-0.0064,"bidPrice":null,"midPrice":null,"askPrice":null,"impactBidPrice":null,"impactMidPrice":null,"impactAskPrice":null,"hasLiquidity":false,"openInterest":null,"openValue":0,"fairMethod":"","fairBasisRate":null,"fairBasis":null,"fairPrice":null,"markMethod":"LastPrice","markPrice":10.79,"indicativeTaxRate":null,"indicativeSettlePrice":null,"optionUnderlyingPrice":null,"settledPrice":null,"timestamp":"2019-07-18T20:35:00.000Z"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "symbol",
            'action': "partial",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'pair': ["XBT", "USD"],
                    'timestamp': _date("2019-07-15T14:47:10.000Z"),
                    'price': 10650,
                    'price24': 10864
                },
                {
                    'symbol': "XBTEUR",
                    'pair': ["XBT", "EUR"],
                    'timestamp': _date("2019-07-18T20:35:00.000Z"),
                    'price': 10.79,
                    'price24': 10.86
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
            'action': "update",
            'data': [
                {
                    'symbol': "XBTUSD",
                    'pair': ["XBT", "USD"],
                    'timestamp': _date("2019-07-01T08:16:15.250Z"),
                    'price': 10933.67,
                    'price24': 10864.0
                }
            ]
        }
    },
]
