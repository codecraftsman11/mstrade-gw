from mst_gateway.connector.api import OrderSchema

DEFAULT_WALLET_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"margin","action":"partial","data":[{"account":379441,"currency":"XBt","riskLimit":1000000000000,"prevState":"","state":"","action":"","amount":1419341,"pendingCredit":0,"pendingDebit":0,"confirmedDebit":0,"prevRealisedPnl":-92,"prevUnrealisedPnl":0,"grossComm":636,"grossOpenCost":0,"grossOpenPremium":0,"grossExecCost":0,"grossMarkValue":0,"riskValue":0,"taxableMargin":0,"initMargin":0,"maintMargin":0,"sessionMargin":0,"targetExcessMargin":0,"varMargin":0,"realisedPnl":-378,"unrealisedPnl":0,"indicativeTax":0,"unrealisedProfit":0,"syntheticMargin":null,"walletBalance":1418963,"marginBalance":1418963,"marginBalancePcnt":1,"marginLeverage":0,"marginUsedPcnt":0,"excessMargin":1418963,"excessMarginPcnt":1,"availableMargin":1418963,"withdrawableMargin":1418963,"grossLastValue":0,"commission":null,"makerFeeDiscount":null,"takerFeeDiscount":null,"timestamp":"2021-12-18T21:54:31.153Z"},{"account":379441,"currency":"USDt","riskLimit":500000000000000,"prevState":"","state":"","action":"","amount":99999981385,"pendingCredit":0,"pendingDebit":0,"confirmedDebit":0,"prevRealisedPnl":0,"prevUnrealisedPnl":0,"grossComm":0,"grossOpenCost":0,"grossOpenPremium":0,"grossExecCost":0,"grossMarkValue":0,"riskValue":0,"taxableMargin":0,"initMargin":0,"maintMargin":0,"sessionMargin":0,"targetExcessMargin":0,"varMargin":0,"realisedPnl":0,"unrealisedPnl":0,"indicativeTax":0,"unrealisedProfit":0,"syntheticMargin":null,"walletBalance":99999981385,"marginBalance":99999981385,"marginBalancePcnt":1,"marginLeverage":0,"marginUsedPcnt":0,"excessMargin":99999981385,"excessMarginPcnt":1,"availableMargin":99999981385,"withdrawableMargin":99999981385,"grossLastValue":0,"commission":null,"makerFeeDiscount":null,"takerFeeDiscount":null,"timestamp":"2021-12-17T06:00:00.101Z"}]}',
            'expect': {
                "wallet": {
                    "acc": "tbitmex",
                    "tb": "wallet",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "bls": [
                                {
                                    "cur": "XBT",
                                    "bl": 0.01418963,
                                    "wbl": 0.01418963,
                                    "upnl": 0.0,
                                    "mbl": 0.01418963,
                                    "mm": 0.0,
                                    "im": 0.0,
                                    "am": 0.01418963,
                                    "t": "hold",
                                }
                            ],
                            "tbl": {"btc": 0.014189630000000002, "usd": 827.163196405},
                            "tupnl": {"btc": 0.0, "usd": 0.0},
                            "tmbl": {"btc": 0.014189630000000002, "usd": 827.163196405},
                        },
                        {
                            "bls": [
                                {
                                    "cur": "USDT",
                                    "bl": 999.99981385,
                                    "wbl": 999.99981385,
                                    "upnl": 0.0,
                                    "mbl": 999.99981385,
                                    "mm": 0.0,
                                    "im": 0.0,
                                    "am": 999.99981385,
                                    "t": "hold",
                                }
                            ],
                            "tbl": {"btc": 0.017154568071054234, "usd": 999.99981385},
                            "tupnl": {"btc": 0.0, "usd": 0.0},
                            "tmbl": {"btc": 0.017154568071054234, "usd": 999.99981385},
                        },
                    ],
                }
            }
        },
        {
            'message': '{"table":"margin","action":"update","data":[{"account":379441,"currency":"XBt","grossOpenPremium":0,"grossMarkValue":212893,"riskValue":212893,"initMargin":0,"maintMargin":2238,"unrealisedPnl":-7,"marginBalance":1418850,"marginBalancePcnt":1,"marginLeverage":0.15004616414702046,"marginUsedPcnt":0.0016,"excessMargin":1416612,"excessMarginPcnt":1,"availableMargin":1416612,"withdrawableMargin":1416612,"timestamp":"2021-12-18T21:59:46.375Z","grossLastValue":212893}]}',
            'expect': {
                "wallet": {
                    "acc": "tbitmex",
                    "tb": "wallet",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "bls": [
                                {
                                    "cur": "XBT",
                                    "bl": None,
                                    "wbl": 0.01416612,
                                    "upnl": -7e-08,
                                    "mbl": 0.0141885,
                                    "mm": 2.238e-05,
                                    "im": 0.0,
                                    "am": 0.01416612,
                                    "t": "trade",
                                }
                            ],
                            "tbl": {"btc": 0.0, "usd": 0.0},
                            "tupnl": {"btc": -7.000000000000002e-08, "usd": -0.0040805450000000005},
                            "tmbl": {"btc": 0.0141885, "usd": 827.09732475},
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"margin","action":"update","data":[{"account":379441,"currency":"XBt","prevRealisedPnl":-137,"grossComm":848,"grossExecCost":0,"grossMarkValue":0,"riskValue":0,"maintMargin":0,"realisedPnl":-515,"unrealisedPnl":0,"walletBalance":1418826,"marginBalance":1418826,"marginLeverage":0,"marginUsedPcnt":0,"excessMargin":1418826,"availableMargin":1418826,"withdrawableMargin":1418826,"timestamp":"2021-12-18T21:59:47.746Z","grossLastValue":0}]}',
            'expect': {
                "wallet": {
                    "acc": "tbitmex",
                    "tb": "wallet",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "bls": [
                                {
                                    "cur": "XBT",
                                    "bl": 0.01418826,
                                    "wbl": 0.01418826,
                                    "upnl": 0.0,
                                    "mbl": 0.01418826,
                                    "mm": 0.0,
                                    "im": 0.0,
                                    "am": 0.01418826,
                                    "t": "hold",
                                }
                            ],
                            "tbl": {"btc": 0.01418826, "usd": 827.0833343099999},
                            "tupnl": {"btc": 0.0, "usd": 0.0},
                            "tmbl": {"btc": 0.01418826, "usd": 827.0833343099999},
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"margin","action":"update","data":[{"account":379441,"currency":"XBt","pendingCredit":100000,"timestamp":"2021-12-18T22:02:04.319Z"}]}',
            'expect': {
                "wallet": {
                    "acc": "tbitmex",
                    "tb": "wallet",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "bls": [
                                {
                                    "cur": "XBT",
                                    "bl": 0.01418826,
                                    "wbl": 0.01418826,
                                    "upnl": None,
                                    "mbl": 0.01418826,
                                    "mm": None,
                                    "im": 0.0,
                                    "am": 0.01418826,
                                    "t": "hold",
                                }
                            ],
                            "tbl": {"btc": 0.01418826, "usd": 827.0833343099999},
                            "tupnl": {"btc": 0.0, "usd": 0.0},
                            "tmbl": {"btc": 0.01418826, "usd": 827.0833343099999},
                        }
                    ],
                }
            }

        }
    ]
}
