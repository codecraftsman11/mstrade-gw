from mst_gateway.connector.api import BUY, SELL, OrderSchema, OrderType, PositionSide, OrderTTL

DEFAULT_SYMBOL = "XBTUSD"
DEFAULT_SYSTEM_SYMBOL = "btcusd"
DEFAULT_SCHEMA = OrderSchema.margin
DEFAULT_ORDER_TYPE = OrderType.limit
DEFAULT_ORDER_SIDE = BUY
DEFAULT_ORDER_OPPOSITE_SIDE = SELL
DEFAULT_ORDER_VOLUME = {
    OrderSchema.margin: 100
}
DEFAULT_ORDER_OPTIONS = {
    'iceberg_volume': 0.0,
    'is_iceberg': False,
    'is_passive': False,
    'comments': "Submitted via API."
}

DEFAULT_ORDER_DATA = {
    OrderSchema.margin: [
        {
            'message': '{"table":"execution","action":"insert","data":[{"execID":"a651bf3c-4410-bee5-adc3-323d87781bbb","orderID":"cf8a2c91-464a-4618-a05f-fb7a57f9a67d","clOrdID":"mst-01GEM0QGEGYJ00NS88TK85BC57","clOrdLinkID":"","account":379441,"symbol":"XBTUSD","side":"Buy","lastQty":null,"lastPx":null,"underlyingLastPx":null,"lastMkt":"","lastLiquidityInd":"","simpleOrderQty":null,"orderQty":100,"price":48844.5,"displayQty":null,"stopPx":null,"pegOffsetValue":null,"pegPriceType":"","currency":"USD","settlCurrency":"XBt","execType":"New","ordType":"Market","timeInForce":"ImmediateOrCancel","execInst":"","contingencyType":"","exDestination":"XBME","ordStatus":"New","triggered":"","workingIndicator":true,"ordRejReason":"","simpleLeavesQty":null,"leavesQty":100,"simpleCumQty":null,"cumQty":0,"avgPx":null,"commission":null,"tradePublishIndicator":"","multiLegReportingType":"SingleSecurity","text":"Submission from testnet.bitmex.com","trdMatchID":"00000000-0000-0000-0000-000000000000","execCost":null,"execComm":null,"homeNotional":null,"foreignNotional":null,"transactTime":"2021-12-21T08:17:02.423Z","timestamp":"2021-12-21T08:17:02.423Z"},{"execID":"eec99810-7a4f-e4b7-9669-e0b5b4189b00","orderID":"cf8a2c91-464a-4618-a05f-fb7a57f9a67d","clOrdID":"mst-01GEM0QGEGYJ00NS88TK85BC57","clOrdLinkID":"","account":379441,"symbol":"XBTUSD","side":"Buy","lastQty":100,"lastPx":48844.5,"underlyingLastPx":null,"lastMkt":"XBME","lastLiquidityInd":"RemovedLiquidity","simpleOrderQty":null,"orderQty":100,"price":48844.5,"displayQty":null,"stopPx":null,"pegOffsetValue":null,"pegPriceType":"","currency":"USD","settlCurrency":"XBt","execType":"Trade","ordType":"Market","timeInForce":"ImmediateOrCancel","execInst":"","contingencyType":"","exDestination":"XBME","ordStatus":"Filled","triggered":"","workingIndicator":false,"ordRejReason":"","simpleLeavesQty":null,"leavesQty":0,"simpleCumQty":null,"cumQty":100,"avgPx":48844.5,"commission":0.0005,"tradePublishIndicator":"PublishTrade","multiLegReportingType":"SingleSecurity","text":"Submission from testnet.bitmex.com","trdMatchID":"9c910adc-7935-1962-cef3-61c80f931ff7","execCost":-204731,"execComm":102,"homeNotional":0.00204731,"foreignNotional":-100,"transactTime":"2021-12-21T08:17:02.423Z","timestamp":"2021-12-21T08:17:02.423Z"}]}',
            'expect': {
                "order": {
                    "acc": "tbitmex",
                    "tb": "order",
                    "sch": OrderSchema.margin,
                    "act": "insert",
                    "d": [
                        {
                            "oid": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                            "eoid": "cf8a2c91-464a-4618-a05f-fb7a57f9a67d",
                            "sd": 0,
                            "ps": PositionSide.both,
                            "tv": 0.0,
                            "tp": 0.0,
                            "vl": 100.0,
                            "p": 48844.5,
                            "st": "pending",
                            "lv": 100.0,
                            "fv": 0.0,
                            "ap": 0.0,
                            "s": "XBTUSD",
                            "stp": 0.0,
                            "tm": "2021-12-21T08:17:02.423000",
                            "t": "market",
                            "ss": "btcusd",
                        },
                        {
                            'oid': 'mst-01GEM0QGEGYJ00NS88TK85BC57',
                            "eoid": "cf8a2c91-464a-4618-a05f-fb7a57f9a67d",
                            "sd": 0,
                            "ps": PositionSide.both,
                            "tv": 100.0,
                            "tp": 48844.5,
                            "vl": 100.0,
                            "p": 48844.5,
                            "st": "closed",
                            "lv": 0.0,
                            "fv": 100.0,
                            "ap": 48844.5,
                            "s": "XBTUSD",
                            "stp": 0.0,
                            "tm": "2021-12-21T08:17:02.423000",
                            "t": "market",
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            'message': '{"table":"execution","action":"insert","data":[{"execID":"e1db2355-1376-e22a-5454-b9e6ae7211ca","orderID":"b46c1aa9-992a-48c5-a953-fd6ef1bff1d0","clOrdID":"mst-01GEM0QGEGYJ00NS88TK85BC57","clOrdLinkID":"","account":379441,"symbol":"XBTUSD","side":"Sell","lastQty":null,"lastPx":null,"underlyingLastPx":null,"lastMkt":"","lastLiquidityInd":"","simpleOrderQty":null,"orderQty":100,"price":48844,"displayQty":null,"stopPx":null,"pegOffsetValue":null,"pegPriceType":"","currency":"USD","settlCurrency":"XBt","execType":"New","ordType":"Market","timeInForce":"ImmediateOrCancel","execInst":"Close","contingencyType":"","exDestination":"XBME","ordStatus":"New","triggered":"","workingIndicator":true,"ordRejReason":"","simpleLeavesQty":null,"leavesQty":100,"simpleCumQty":null,"cumQty":0,"avgPx":null,"commission":null,"tradePublishIndicator":"","multiLegReportingType":"SingleSecurity","text":"Position Close from testnet.bitmex.com","trdMatchID":"00000000-0000-0000-0000-000000000000","execCost":null,"execComm":null,"homeNotional":null,"foreignNotional":null,"transactTime":"2021-12-21T08:18:00.153Z","timestamp":"2021-12-21T08:18:00.153Z"},{"execID":"89811ff3-4f10-b399-44d6-9043ba91c40c","orderID":"b46c1aa9-992a-48c5-a953-fd6ef1bff1d0","clOrdID":"mst-01GEM0QGEGYJ00NS88TK85BC57","clOrdLinkID":"","account":379441,"symbol":"XBTUSD","side":"Sell","lastQty":100,"lastPx":48844,"underlyingLastPx":null,"lastMkt":"XBME","lastLiquidityInd":"RemovedLiquidity","simpleOrderQty":null,"orderQty":100,"price":48844,"displayQty":null,"stopPx":null,"pegOffsetValue":null,"pegPriceType":"","currency":"USD","settlCurrency":"XBt","execType":"Trade","ordType":"Market","timeInForce":"ImmediateOrCancel","execInst":"Close","contingencyType":"","exDestination":"XBME","ordStatus":"Filled","triggered":"","workingIndicator":false,"ordRejReason":"","simpleLeavesQty":null,"leavesQty":0,"simpleCumQty":null,"cumQty":100,"avgPx":48844,"commission":0.0005,"tradePublishIndicator":"PublishTrade","multiLegReportingType":"SingleSecurity","text":"Position Close from testnet.bitmex.com","trdMatchID":"b94c98b5-5ba6-0b71-82f3-f3f350d26ffe","execCost":204733,"execComm":102,"homeNotional":-0.00204733,"foreignNotional":100,"transactTime":"2021-12-21T08:18:00.153Z","timestamp":"2021-12-21T08:18:00.153Z"}]}',
            'expect': {
                "order": {
                    "acc": "tbitmex",
                    "tb": "order",
                    "sch": OrderSchema.margin,
                    "act": "insert",
                    "d": [
                        {
                            "oid": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                            "eoid": "b46c1aa9-992a-48c5-a953-fd6ef1bff1d0",
                            "sd": 1,
                            "ps": PositionSide.both,
                            "tv": 0.0,
                            "tp": 0.0,
                            "vl": 100.0,
                            "p": 48844.0,
                            "st": "pending",
                            "lv": 100.0,
                            "fv": 0.0,
                            "ap": 0.0,
                            "s": "XBTUSD",
                            "stp": 0.0,
                            "tm": "2021-12-21T08:18:00.153000",
                            "t": "market",
                            "ss": "btcusd",
                        },
                        {
                            "oid": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                            "eoid": "b46c1aa9-992a-48c5-a953-fd6ef1bff1d0",
                            "sd": 1,
                            "ps": PositionSide.both,
                            "tv": 100.0,
                            "tp": 48844.0,
                            "vl": 100.0,
                            "p": 48844.0,
                            "st": "closed",
                            "lv": 0.0,
                            "fv": 100.0,
                            "ap": 48844.0,
                            "s": "XBTUSD",
                            "stp": 0.0,
                            "tm": "2021-12-21T08:18:00.153000",
                            "t": "market",
                            "ss": "btcusd",
                        },
                    ],
                }
            }

        }
    ]
}

DEFAULT_ORDER_SPLIT_DATA = {
    OrderSchema.margin: [
        [
            {
                "table": "execution",
                "action": "insert",
                "data": [
                    {
                        "execID": "a651bf3c-4410-bee5-adc3-323d87781bbb",
                        "orderID": "cf8a2c91-464a-4618-a05f-fb7a57f9a67d",
                        "clOrdID": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                        "clOrdLinkID": "",
                        "account": 379441,
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "lastQty": None,
                        "lastPx": None,
                        "underlyingLastPx": None,
                        "lastMkt": "",
                        "lastLiquidityInd": "",
                        "simpleOrderQty": None,
                        "orderQty": 100,
                        "price": 48844.5,
                        "displayQty": None,
                        "stopPx": None,
                        "pegOffsetValue": None,
                        "pegPriceType": "",
                        "currency": "USD",
                        "settlCurrency": "XBt",
                        "execType": "New",
                        "ordType": "Market",
                        "timeInForce": "ImmediateOrCancel",
                        "execInst": "",
                        "contingencyType": "",
                        "exDestination": "XBME",
                        "ordStatus": "New",
                        "triggered": "",
                        "workingIndicator": True,
                        "ordRejReason": "",
                        "simpleLeavesQty": None,
                        "leavesQty": 100,
                        "simpleCumQty": None,
                        "cumQty": 0,
                        "avgPx": None,
                        "commission": None,
                        "tradePublishIndicator": "",
                        "multiLegReportingType": "SingleSecurity",
                        "text": "Submission from testnet.bitmex.com",
                        "trdMatchID": "00000000-0000-0000-0000-000000000000",
                        "execCost": None,
                        "execComm": None,
                        "homeNotional": None,
                        "foreignNotional": None,
                        "transactTime": "2021-12-21T08:17:02.423Z",
                        "timestamp": "2021-12-21T08:17:02.423Z",
                    }
                ],
            },
            {
                "table": "execution",
                "action": "delete",
                "data": [
                    {
                        "execID": "eec99810-7a4f-e4b7-9669-e0b5b4189b00",
                        "orderID": "cf8a2c91-464a-4618-a05f-fb7a57f9a67d",
                        "clOrdID": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                        "clOrdLinkID": "",
                        "account": 379441,
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "lastQty": 100,
                        "lastPx": 48844.5,
                        "underlyingLastPx": None,
                        "lastMkt": "XBME",
                        "lastLiquidityInd": "RemovedLiquidity",
                        "simpleOrderQty": None,
                        "orderQty": 100,
                        "price": 48844.5,
                        "displayQty": None,
                        "stopPx": None,
                        "pegOffsetValue": None,
                        "pegPriceType": "",
                        "currency": "USD",
                        "settlCurrency": "XBt",
                        "execType": "Trade",
                        "ordType": "Market",
                        "timeInForce": "ImmediateOrCancel",
                        "execInst": "",
                        "contingencyType": "",
                        "exDestination": "XBME",
                        "ordStatus": "Filled",
                        "triggered": "",
                        "workingIndicator": False,
                        "ordRejReason": "",
                        "simpleLeavesQty": None,
                        "leavesQty": 0,
                        "simpleCumQty": None,
                        "cumQty": 100,
                        "avgPx": 48844.5,
                        "commission": 0.0005,
                        "tradePublishIndicator": "PublishTrade",
                        "multiLegReportingType": "SingleSecurity",
                        "text": "Submission from testnet.bitmex.com",
                        "trdMatchID": "9c910adc-7935-1962-cef3-61c80f931ff7",
                        "execCost": -204731,
                        "execComm": 102,
                        "homeNotional": 0.00204731,
                        "foreignNotional": -100,
                        "transactTime": "2021-12-21T08:17:02.423Z",
                        "timestamp": "2021-12-21T08:17:02.423Z",
                    }
                ],
            },
        ],
        [
            {
                "table": "execution",
                "action": "insert",
                "data": [
                    {
                        "execID": "e1db2355-1376-e22a-5454-b9e6ae7211ca",
                        "orderID": "b46c1aa9-992a-48c5-a953-fd6ef1bff1d0",
                        "clOrdID": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                        "clOrdLinkID": "",
                        "account": 379441,
                        "symbol": "XBTUSD",
                        "side": "Sell",
                        "lastQty": None,
                        "lastPx": None,
                        "underlyingLastPx": None,
                        "lastMkt": "",
                        "lastLiquidityInd": "",
                        "simpleOrderQty": None,
                        "orderQty": 100,
                        "price": 48844,
                        "displayQty": None,
                        "stopPx": None,
                        "pegOffsetValue": None,
                        "pegPriceType": "",
                        "currency": "USD",
                        "settlCurrency": "XBt",
                        "execType": "New",
                        "ordType": "Market",
                        "timeInForce": "ImmediateOrCancel",
                        "execInst": "Close",
                        "contingencyType": "",
                        "exDestination": "XBME",
                        "ordStatus": "New",
                        "triggered": "",
                        "workingIndicator": True,
                        "ordRejReason": "",
                        "simpleLeavesQty": None,
                        "leavesQty": 100,
                        "simpleCumQty": None,
                        "cumQty": 0,
                        "avgPx": None,
                        "commission": None,
                        "tradePublishIndicator": "",
                        "multiLegReportingType": "SingleSecurity",
                        "text": "Position Close from testnet.bitmex.com",
                        "trdMatchID": "00000000-0000-0000-0000-000000000000",
                        "execCost": None,
                        "execComm": None,
                        "homeNotional": None,
                        "foreignNotional": None,
                        "transactTime": "2021-12-21T08:18:00.153Z",
                        "timestamp": "2021-12-21T08:18:00.153Z",
                    }
                ],
            },
            {
                "table": "execution",
                "action": "delete",
                "data": [
                    {
                        "execID": "89811ff3-4f10-b399-44d6-9043ba91c40c",
                        "orderID": "b46c1aa9-992a-48c5-a953-fd6ef1bff1d0",
                        "clOrdID": "mst-01GEM0QGEGYJ00NS88TK85BC57",
                        "clOrdLinkID": "",
                        "account": 379441,
                        "symbol": "XBTUSD",
                        "side": "Sell",
                        "lastQty": 100,
                        "lastPx": 48844,
                        "underlyingLastPx": None,
                        "lastMkt": "XBME",
                        "lastLiquidityInd": "RemovedLiquidity",
                        "simpleOrderQty": None,
                        "orderQty": 100,
                        "price": 48844,
                        "displayQty": None,
                        "stopPx": None,
                        "pegOffsetValue": None,
                        "pegPriceType": "",
                        "currency": "USD",
                        "settlCurrency": "XBt",
                        "execType": "Trade",
                        "ordType": "Market",
                        "timeInForce": "ImmediateOrCancel",
                        "execInst": "Close",
                        "contingencyType": "",
                        "exDestination": "XBME",
                        "ordStatus": "Filled",
                        "triggered": "",
                        "workingIndicator": False,
                        "ordRejReason": "",
                        "simpleLeavesQty": None,
                        "leavesQty": 0,
                        "simpleCumQty": None,
                        "cumQty": 100,
                        "avgPx": 48844,
                        "commission": 0.0005,
                        "tradePublishIndicator": "PublishTrade",
                        "multiLegReportingType": "SingleSecurity",
                        "text": "Position Close from testnet.bitmex.com",
                        "trdMatchID": "b94c98b5-5ba6-0b71-82f3-f3f350d26ffe",
                        "execCost": 204733,
                        "execComm": 102,
                        "homeNotional": -0.00204733,
                        "foreignNotional": 100,
                        "transactTime": "2021-12-21T08:18:00.153Z",
                        "timestamp": "2021-12-21T08:18:00.153Z",
                    }
                ],
            },
        ]
    ]
}

DEFAULT_ORDER = {
    OrderSchema.margin: {
        'filled_volume': 0.0,
        'schema': OrderSchema.margin,
        'side': DEFAULT_ORDER_SIDE,
        'position_side': PositionSide.both,
        'stop_price': 0.0,
        'symbol': DEFAULT_SYMBOL,
        'system_symbol': DEFAULT_SYSTEM_SYMBOL,
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.margin],
        'ttl': OrderTTL.GTC,
        'iceberg_volume': 0.0,
        'is_iceberg': False,
        'is_passive': False,
        'comments': "Submitted via API."
    }
}
