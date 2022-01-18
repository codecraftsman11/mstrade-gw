from mst_gateway.connector.api import OrderSchema

DEFAULT_POSITION_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"position","action":"partial","data":[{"account":379441,"symbol":"XBTUSD","currency":"XBt","underlying":"XBT","quoteCurrency":"USD","commission":0.0005,"initMarginReq":0.01,"maintMarginReq":0.0035,"riskLimit":20000000000,"leverage":100,"crossMargin":true,"deleveragePercentile":null,"rebalancedPnl":286,"prevRealisedPnl":-74,"prevUnrealisedPnl":0,"prevClosePrice":47090.75,"openingTimestamp":"2021-12-18T21:00:00.000Z","openingQty":0,"openingCost":0,"openingComm":0,"openOrderBuyQty":0,"openOrderBuyCost":0,"openOrderBuyPremium":0,"openOrderSellQty":0,"openOrderSellCost":0,"openOrderSellPremium":0,"execBuyQty":200,"execBuyCost":425677,"execSellQty":200,"execSellCost":425539,"execQty":0,"execCost":-138,"execComm":424,"currentTimestamp":"2021-12-18T21:47:29.045Z","currentQty":0,"currentCost":-138,"currentComm":424,"realisedCost":-138,"unrealisedCost":0,"grossOpenCost":0,"grossOpenPremium":0,"grossExecCost":0,"isOpen":false,"markPrice":null,"markValue":0,"riskValue":0,"homeNotional":0,"foreignNotional":0,"posState":"","posCost":0,"posCost2":0,"posCross":0,"posInit":0,"posComm":0,"posLoss":0,"posMargin":0,"posMaint":0,"posAllowance":0,"taxableMargin":0,"initMargin":0,"maintMargin":0,"sessionMargin":0,"targetExcessMargin":0,"varMargin":0,"realisedGrossPnl":138,"realisedTax":0,"realisedPnl":-286,"unrealisedGrossPnl":0,"longBankrupt":0,"shortBankrupt":0,"taxBase":0,"indicativeTaxRate":null,"indicativeTax":0,"unrealisedTax":0,"unrealisedPnl":0,"unrealisedPnlPcnt":0,"unrealisedRoePcnt":0,"simpleQty":null,"simpleCost":null,"simpleValue":null,"simplePnl":null,"simplePnlPcnt":null,"avgCostPrice":null,"avgEntryPrice":null,"breakEvenPrice":null,"marginCallPrice":null,"liquidationPrice":null,"bankruptPrice":null,"timestamp":"2021-12-18T21:47:29.045Z","lastPrice":null,"lastValue":0}]}',
            'expect': {
                "position": {
                    "acc": "tbitmex",
                    "tb": "position",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "tm": "2021-12-18T21:47:29.045000",
                            "s": "XBTUSD",
                            "mp": 0.0,
                            "upnl": {
                                "base": 0.0,
                                "btc": 0.0,
                                "usd": 0.0
                            },
                            "vl": 0.0,
                            "lp": 0.0,
                            "ep": 0.0,
                            "sd": None,
                            "lvrp": "cross",
                            "lvr": 100.0,
                            "act": "update",
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"position","action":"update","data":[{"account":379441,"symbol":"XBTUSD","rebalancedPnl":286,"prevRealisedPnl":-74,"execBuyQty":300,"execBuyCost":638552,"execQty":100,"execCost":-213013,"execComm":530,"currentTimestamp":"2021-12-18T21:53:44.928Z","currentQty":100,"currentCost":-213013,"currentComm":530,"unrealisedCost":-212875,"grossExecCost":212851,"isOpen":true,"markPrice":46959.18,"markValue":-212951,"riskValue":212951,"homeNotional":0.00212951,"foreignNotional":-100,"posCost":-212875,"posCost2":-212875,"posInit":2129,"posComm":108,"posMargin":2237,"posMaint":875,"maintMargin":2161,"realisedPnl":-392,"unrealisedGrossPnl":-76,"unrealisedPnl":-76,"unrealisedPnlPcnt":-0.0004,"unrealisedRoePcnt":-0.0357,"avgCostPrice":46976,"avgEntryPrice":46976,"breakEvenPrice":46999.5,"marginCallPrice":6125.5,"liquidationPrice":6125.5,"bankruptPrice":6122.5,"timestamp":"2021-12-18T21:53:44.928Z","lastPrice":46959.18,"lastValue":-212951,"currency":"XBt"}]}',
            'expect': {
                "position": {
                    "acc": "tbitmex",
                    "tb": "position",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-18T21:53:44.928000",
                            "s": "XBTUSD",
                            "mp": 46959.18,
                            "upnl": {
                                "base": -7.6e-07,
                                "btc": -7.6e-07,
                                "usd": -0.04430306
                            },
                            "vl": 100.0,
                            "lp": 6125.5,
                            "ep": 46976.0,
                            "sd": 0,
                            "lvrp": "cross",
                            "lvr": 100.0,
                            "act": "create",
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"position","action":"update","data":[{"account":379441,"symbol":"XBTUSD","deleveragePercentile":1,"currency":"XBt","currentQty":100,"markPrice":46959.18,"liquidationPrice":6125.5,"timestamp":"2021-12-18T21:53:44.928Z"}]}',
            'expect': {
                "position": {
                    "acc": "tbitmex",
                    "tb": "position",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-18T21:53:44.928000",
                            "s": "XBTUSD",
                            "mp": 46959.18,
                            "upnl": {
                                "base": -7.6e-07,
                                "btc": -7.6e-07,
                                "usd": -0.04430306
                            },
                            "vl": 100.0,
                            "lp": 6125.5,
                            "ep": 46976.0,
                            "sd": 0,
                            "lvrp": "cross",
                            "lvr": 100.0,
                            "act": "update",
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"position","action":"update","data":[{"account":379441,"symbol":"XBTUSD","openOrderBuyPremium":0,"openOrderSellPremium":0,"currentTimestamp":"2021-12-18T21:53:46.376Z","grossOpenPremium":0,"markPrice":46960.3,"markValue":-212946,"riskValue":212946,"homeNotional":0.00212946,"foreignNotional":-100,"posCross":71,"posComm":109,"posMargin":2309,"posMaint":876,"initMargin":0,"maintMargin":2238,"unrealisedGrossPnl":-71,"unrealisedPnl":-71,"unrealisedPnlPcnt":-0.0003,"unrealisedRoePcnt":-0.0334,"marginCallPrice":6134.5,"liquidationPrice":6134.5,"bankruptPrice":6131.5,"timestamp":"2021-12-18T21:53:46.376Z","lastPrice":46960.3,"lastValue":-212946,"currency":"XBt","currentQty":100}]}',
            'expect': {
                "position": {
                    "acc": "tbitmex",
                    "tb": "position",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-18T21:53:46.376000",
                            "s": "XBTUSD",
                            "mp": 46960.3,
                            "upnl": {
                                "base": -7.1e-07,
                                "btc": -7.1e-07,
                                "usd": -0.041388385
                            },
                            "vl": 100.0,
                            "lp": 6134.5,
                            "ep": 46976.0,
                            "sd": 0,
                            "lvrp": "cross",
                            "lvr": 100.0,
                            "act": "update",
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        }
    ]
}
