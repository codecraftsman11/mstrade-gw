from mst_gateway.connector.api import OrderSchema

DEFAULT_TRADE_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"trade","action":"partial","data":[{"timestamp":"2021-12-16T08:24:16.415Z","symbol":"XBTUSD","side":"Buy","size":100,"price":48699.5,"tickDirection":"ZeroPlusTick","trdMatchID":"01fdfa2d-0979-5c87-4d8e-ab5e4ea77e50","grossValue":205341,"homeNotional":0.00205341,"foreignNotional":100},{"timestamp":"2021-12-16T08:01:31.049Z","symbol":"XBTUSD","side":"Sell","size":1000,"price":51377,"tickDirection":"MinusTick","trdMatchID":"1f5dd12a-efd2-f370-435e-d21bdf00d9c8","grossValue":51377000,"homeNotional":0.001,"foreignNotional":51.377},{"timestamp":"2021-12-16T08:04:32.049Z","symbol":"XBTUSD","side":"Buy","size":8000,"price":49201,"tickDirection":"PlusTick","trdMatchID":"36891d7e-0bc7-1275-1f5b-866b5b2a00bc","grossValue":393608000,"homeNotional":0.008,"foreignNotional":393.608}]}',
            'expect': {
                "trade": {
                    "acc": "tbitmex",
                    "tb": "trade",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "tm": "2021-12-16T08:24:16.415000",
                            "s": "XBTUSD",
                            "p": 48699.5,
                            "vl": 100,
                            "sd": 0,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:01:31.049000",
                            "s": "XBTUSD",
                            "p": 51377.0,
                            "vl": 1000,
                            "sd": 1,
                            "ss": "btcusd",
                        },
                        {
                            "tm": "2021-12-16T08:04:32.049000",
                            "s": "XBTUSD",
                            "p": 49201.0,
                            "vl": 8000,
                            "sd": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            'message': '{"table":"trade","action":"insert","data":[{"timestamp":"2021-12-16T08:29:20.595Z","symbol":"XBTUSD","side":"Buy","size":100,"price":48699.5,"tickDirection":"ZeroPlusTick","trdMatchID":"cfb5f035-ee9b-0a94-4f00-877684dde1e0","grossValue":205341,"homeNotional":0.00205341,"foreignNotional":100}]}',
            'expect': {
                "trade": {
                    "acc": "tbitmex",
                    "tb": "trade",
                    "sch": "margin1",
                    "act": "insert",
                    "d": [
                        {
                            "tm": "2021-12-16T08:29:20.595000",
                            "s": "XBTUSD",
                            "p": 48699.5,
                            "vl": 100,
                            "sd": 0,
                            "ss": "btcusd",
                        }
                    ],
                }
            }

        }
    ]
}

DEFAULT_TRADE_SPLIT_DATA = {
    OrderSchema.margin1: [
        [
            {
                "table": "trade",
                "action": "partial",
                "data": [
                    {
                        "timestamp": "2021-12-16T08:24:16.415Z",
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "size": 100,
                        "price": 48699.5,
                        "tickDirection": "ZeroPlusTick",
                        "trdMatchID": "01fdfa2d-0979-5c87-4d8e-ab5e4ea77e50",
                        "grossValue": 205341,
                        "homeNotional": 0.00205341,
                        "foreignNotional": 100,
                    }
                ],
            },
            {
                "table": "trade",
                "action": "partial",
                "data": [
                    {
                        "timestamp": "2021-12-16T08:01:31.049Z",
                        "symbol": "XBTUSD",
                        "side": "Sell",
                        "size": 1000,
                        "price": 51377,
                        "tickDirection": "MinusTick",
                        "trdMatchID": "1f5dd12a-efd2-f370-435e-d21bdf00d9c8",
                        "grossValue": 51377000,
                        "homeNotional": 0.001,
                        "foreignNotional": 51.377,
                    }
                ],
            },
            {
                "table": "trade",
                "action": "partial",
                "data": [
                    {
                        "timestamp": "2021-12-16T08:04:32.049Z",
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "size": 8000,
                        "price": 49201,
                        "tickDirection": "PlusTick",
                        "trdMatchID": "36891d7e-0bc7-1275-1f5b-866b5b2a00bc",
                        "grossValue": 393608000,
                        "homeNotional": 0.008,
                        "foreignNotional": 393.608,
                    }
                ],
            },
        ],
        [
            {
                "table": "trade",
                "action": "insert",
                "data": [
                    {
                        "timestamp": "2021-12-16T08:29:20.595Z",
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "size": 100,
                        "price": 48699.5,
                        "tickDirection": "ZeroPlusTick",
                        "trdMatchID": "cfb5f035-ee9b-0a94-4f00-877684dde1e0",
                        "grossValue": 205341,
                        "homeNotional": 0.00205341,
                        "foreignNotional": 100,
                    }
                ],
            }
        ]
    ]
}