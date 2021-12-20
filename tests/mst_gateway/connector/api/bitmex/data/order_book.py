from mst_gateway.connector.api import OrderSchema

DEFAULT_ORDER_BOOK_DATA = {
    OrderSchema.margin1: [
        {
            'message': '{"table":"orderBookL2_25","action":"partial","data":[{"symbol":"XBTUSD","id":15595080250,"side":"Sell","size":99400,"price":49197.5},{"symbol":"XBTUSD","id":15595348050,"side":"Buy","size":5000,"price":46435}]}',
            'expect': {
                "order_book": {
                    "acc": "tbitmex",
                    "tb": "order_book",
                    "sch": "margin1",
                    "act": "partial",
                    "d": [
                        {
                            "id": 98395,
                            "s": "XBTUSD",
                            "p": 49197.5,
                            "vl": 99400,
                            "sd": 1,
                            "ss": "btcusd",
                        },
                        {
                            "id": 92870,
                            "s": "XBTUSD",
                            "p": 46435.0,
                            "vl": 5000,
                            "sd": 0,
                            "ss": "btcusd",
                        },
                    ],
                }
            }
        },
        {
            'message': '{"table":"orderBookL2_25","action":"insert","data":[{"symbol":"XBTUSD","id":15595104300,"side":"Sell","size":500,"price":48957}]}',
            'expect': {
                "order_book": {
                    "acc": "tbitmex",
                    "tb": "order_book",
                    "sch": "margin1",
                    "act": "insert",
                    "d": [
                        {
                            "id": 97914,
                            "s": "XBTUSD",
                            "p": 48957.0,
                            "vl": 500,
                            "sd": 1,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        },
        {
            'message': '{"table":"orderBookL2_25","action":"update","data":[{"symbol":"XBTUSD","id":15595334100,"side":"Buy","size":94300}]}',
            'expect': {
                "order_book": {
                    "acc": "tbitmex",
                    "tb": "order_book",
                    "sch": "margin1",
                    "act": "update",
                    "d": [
                        {
                            "id": None,
                            "s": "XBTUSD",
                            "p": None,
                            "vl": 94300,
                            "sd": 0,
                            "ss": "btcusd"
                        }
                    ],
                }
            },
        },
        {
            'message': '{"table":"orderBookL2_25","action":"delete","data":[{"symbol":"XBTUSD","id":15595348050,"side":"Buy"}]}',
            'expect': {
                "order_book": {
                    "acc": "tbitmex",
                    "tb": "order_book",
                    "sch": "margin1",
                    "act": "delete",
                    "d": [
                        {
                            "id": 92870,
                            "s": "XBTUSD",
                            "p": 46435.0,
                            "vl": None,
                            "sd": 0,
                            "ss": "btcusd",
                        }
                    ],
                }
            }
        }
    ]
}

DEFAULT_ORDER_BOOK_MESSAGES = {
    OrderSchema.margin1: [
        {
            "table": "orderBookL2_25",
            "action": "partial",
            "data": [
                {
                    "symbol": "XBTUSD",
                    "id": 15595080250,
                    "side": "Sell",
                    "size": 99400,
                    "price": 49197.5
                },
                {
                    "symbol": "XBTUSD",
                    "id": 15595348050,
                    "side": "Buy",
                    "size": 5000,
                    "price": 46435
                },
            ]
        },
        {
            "table": "orderBookL2_25",
            "action": "insert",
            "data": [
                {
                    "symbol": "XBTUSD",
                    "id": 15595104300,
                    "side": "Sell",
                    "size": 500,
                    "price": 48957
                }
            ]
        },
        {
            "table": "orderBookL2_25",
            "action": "update",
            "data": [
                {
                    "symbol": "XBTUSD",
                    "id": 15595334100,
                    "side": "Buy",
                    "size": 94300
                }
            ]
        },
        {
            "table": "orderBookL2_25",
            "action": "delete",
            "data": [
                {
                    "symbol": "XBTUSD",
                    "id": 15595348050,
                    "side": "Buy"
                }
            ]
        },
    ]
}
