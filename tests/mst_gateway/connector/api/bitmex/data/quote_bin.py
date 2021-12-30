from mst_gateway.connector.api import OrderSchema

DEFAULT_QUOTE_BIN_DATA = {
    OrderSchema.margin1: [
        {
            "message": '{"table":"tradeBin1m","action":"partial","data":[{"timestamp":"2021-12-28T13:04:59.000Z","symbol":"XBTUSD","open":49120.5,"high":49120.5,"low":49120.5,"close":49120.5,"trades":2,"volume":200,"vwap":49120.5,"lastSize":100,"turnover":407162,"homeNotional":0.00407162,"foreignNotional":200}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "tm": "2021-12-28T13:03:59.999999",
                            "s": "XBTUSD",
                            "opp": 49120.5,
                            "clp": 49120.5,
                            "hip": 49120.5,
                            "lop": 49120.5,
                            "vl": 200,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-28T13:04:00.000000",
                            "s": "XBTUSD",
                            "opp": 49120.5,
                            "clp": 49120.5,
                            "hip": 49120.5,
                            "lop": 49120.5,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"partial","data":[{"timestamp":"2021-12-28T13:06:16.632Z","symbol":"XBTUSD","side":"Buy","size":100,"price":48938.5,"tickDirection":"ZeroMinusTick","trdMatchID":"5fc73cf3-7651-d392-a2ef-c071ff4493fa","grossValue":204338,"homeNotional":0.00204338,"foreignNotional":100}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:06:16.632000",
                            "opp": 48938.5,
                            "clp": 48938.5,
                            "hip": 48938.5,
                            "lop": 48938.5,
                            "vl": 100,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-28T13:06:57.099Z","symbol":"XBTUSD","side":"Sell","size":400,"price":48938,"tickDirection":"MinusTick","trdMatchID":"150667c3-5bc7-e45f-1b30-be0231a10636","grossValue":817360,"homeNotional":0.0081736,"foreignNotional":400}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:06:57.099000",
                            "opp": 48938.5,
                            "clp": 48938.0,
                            "hip": 48938.5,
                            "lop": 48938.0,
                            "vl": 500,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-28T13:06:57.099Z","symbol":"XBTUSD","side":"Sell","size":100,"price":48938,"tickDirection":"ZeroMinusTick","trdMatchID":"86d2028a-259a-4bd9-6283-9c9df6048fdf","grossValue":204340,"homeNotional":0.0020434,"foreignNotional":100}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:06:57.099000",
                            "opp": 48938.5,
                            "clp": 48938.0,
                            "hip": 48938.5,
                            "lop": 48938.0,
                            "vl": 600,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-28T13:06:57.099Z","symbol":"XBTUSD","side":"Sell","size":500,"price":48895.5,"tickDirection":"MinusTick","trdMatchID":"f6f48f7a-3cd2-c332-075e-1ec7ee85f0a7","grossValue":1022590,"homeNotional":0.0102259,"foreignNotional":500}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:06:57.099000",
                            "opp": 48938.5,
                            "clp": 48895.5,
                            "hip": 48938.5,
                            "lop": 48895.5,
                            "vl": 1100,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2021-12-28T13:05:59.000Z","symbol":"XBTUSD","open":49120.5,"high":49120,"low":48895.5,"close":48895.5,"trades":13,"volume":4300,"vwap":49020.8,"lastSize":500,"turnover":8771785,"homeNotional":0.08771785,"foreignNotional":4300}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-28T13:04:59.999999",
                            "s": "XBTUSD",
                            "opp": 49120.5,
                            "clp": 48895.5,
                            "hip": 49120.0,
                            "lop": 48895.5,
                            "vl": 4300,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-28T13:05:00.000000",
                            "s": "XBTUSD",
                            "opp": 48895.5,
                            "clp": 48895.5,
                            "hip": 48895.5,
                            "lop": 48895.5,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-28T13:07:16.714Z","symbol":"XBTUSD","side":"Buy","size":100,"price":48949.5,"tickDirection":"PlusTick","trdMatchID":"1c744c95-4927-d019-b45c-88ea0a3b57c0","grossValue":204292,"homeNotional":0.00204292,"foreignNotional":100}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:07:16.714000",
                            "opp": 48895.5,
                            "clp": 48949.5,
                            "hip": 48949.5,
                            "lop": 48895.5,
                            "vl": 100,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-28T13:07:16.721Z","symbol":"XBTUSD","side":"Buy","size":200,"price":48949.5,"tickDirection":"ZeroPlusTick","trdMatchID":"3565bf42-4d4d-63e6-dc51-4154fbd19fa0","grossValue":408584,"homeNotional":0.00408584,"foreignNotional":200}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "s": "XBTUSD",
                            "tm": "2021-12-28T13:07:16.721000",
                            "opp": 48895.5,
                            "clp": 48949.5,
                            "hip": 48949.5,
                            "lop": 48895.5,
                            "vl": 300,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            "message": '{"table":"tradeBin1m","action":"insert","data":[{"timestamp":"2021-12-28T13:06:59.000Z","symbol":"XBTUSD","open":48895.5,"high":48949.5,"low":48949.5,"close":48949.5,"trades":2,"volume":300,"vwap":48949.5,"lastSize":200,"turnover":612876,"homeNotional":0.0061287600000000005,"foreignNotional":300}]}',
            "expect": {
                "quote_bin": {
                    "acc": "tbitmex",
                    "tb": "quote_bin",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "tm": "2021-12-28T13:05:59.999999",
                            "s": "XBTUSD",
                            "opp": 48895.5,
                            "clp": 48949.5,
                            "hip": 48949.5,
                            "lop": 48949.5,
                            "vl": 300,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-28T13:06:00.000000",
                            "s": "XBTUSD",
                            "opp": 48949.5,
                            "clp": 48949.5,
                            "hip": 48949.5,
                            "lop": 48949.5,
                            "vl": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        }
    ]
}
