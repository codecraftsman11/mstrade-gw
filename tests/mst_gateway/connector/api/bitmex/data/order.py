from mst_gateway.connector.api import BUY, SELL, OrderSchema, OrderExec, OrderType

DEFAULT_SYMBOL = "XBTUSD"
DEFAULT_SYSTEM_SYMBOL = "btcusd"
DEFAULT_SCHEMA = OrderSchema.margin1
DEFAULT_ORDER_TYPE = OrderType.limit
DEFAULT_ORDER_SIDE = BUY
DEFAULT_ORDER_OPPOSITE_SIDE = SELL
DEFAULT_ORDER_VOLUME = {
    OrderSchema.margin1: 100
}
DEFAULT_ORDER_OPTIONS = {}

DEFAULT_ORDER_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"order","action":"insert","data":[{"orderID":"89d75e7f-d851-4eea-b774-7b74ce2692eb","clOrdID":"","clOrdLinkID":"","account":379441,"symbol":"XBTUSD","side":"Buy","simpleOrderQty":null,"orderQty":100,"price":46545,"displayQty":null,"stopPx":null,"pegOffsetValue":null,"pegPriceType":"","currency":"USD","settlCurrency":"XBt","ordType":"Limit","timeInForce":"GoodTillCancel","execInst":"","contingencyType":"","exDestination":"XBME","ordStatus":"New","triggered":"","workingIndicator":true,"ordRejReason":"","simpleLeavesQty":null,"leavesQty":100,"simpleCumQty":null,"cumQty":0,"avgPx":null,"multiLegReportingType":"SingleSecurity","text":"Submission from testnet.bitmex.com","transactTime":"2021-12-18T21:43:05.284Z","timestamp":"2021-12-18T21:43:05.284Z"}]}',
            'expect': {
                "order": {
                    "acc": "tbitmex",
                    "tb": "order",
                    "sch": "margin1",
                    "act": "insert",
                    "d": [
                        {
                            "eoid": "89d75e7f-d851-4eea-b774-7b74ce2692eb",
                            "sd": 0,
                            "tv": None,
                            "tp": None,
                            "vl": 100.0,
                            "p": 46545.0,
                            "st": "pending",
                            "lv": 100.0,
                            "fv": 0.0,
                            "ap": None,
                            "s": "XBTUSD",
                            "stp": None,
                            "tm": "2021-12-18T21:43:05.284000",
                            "t": "limit",
                            "exc": "limit",
                            "ss": "btcusd",
                        }
                    ],
                }
            }

        }
    ]
}

DEFAULT_ORDER_SPLIT_DATA = {
    OrderSchema.margin1: [
        [
            {
                "table": "order",
                "action": "insert",
                "data": [
                    {
                        "orderID": "89d75e7f-d851-4eea-b774-7b74ce2692eb",
                        "clOrdID": "",
                        "clOrdLinkID": "",
                        "account": 379441,
                        "symbol": "XBTUSD",
                        "side": "Buy",
                        "simpleOrderQty": None,
                        "orderQty": 100,
                        "price": 46545,
                        "displayQty": None,
                        "stopPx": None,
                        "pegOffsetValue": None,
                        "pegPriceType": "",
                        "currency": "USD",
                        "settlCurrency": "XBt",
                        "ordType": "Limit",
                        "timeInForce": "GoodTillCancel",
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
                        "multiLegReportingType": "SingleSecurity",
                        "text": "Submission from testnet.bitmex.com",
                        "transactTime": "2021-12-18T21:43:05.284Z",
                        "timestamp": "2021-12-18T21:43:05.284Z",
                    }
                ],
            }
        ]
    ]
}

DEFAULT_ORDER = {
    OrderSchema.margin1: {
        'execution': OrderExec.limit,
        'filled_volume': 0.0,
        'schema': OrderSchema.margin1,
        'side': DEFAULT_ORDER_SIDE,
        'stop': None,
        'symbol': DEFAULT_SYMBOL,
        'system_symbol': DEFAULT_SYSTEM_SYMBOL,
        'type': OrderType.limit,
        'volume': DEFAULT_ORDER_VOLUME[OrderSchema.margin1],
    }
}
