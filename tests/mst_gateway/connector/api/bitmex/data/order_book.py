from mst_gateway.connector.api import BUY, SELL


TEST_ORDER_BOOK_MESSAGES = [
    {
        'message': '{"table": "orderBookL2_25", "action": "invalid"}',
        'data': None,
    },
    {
        'message': '{"table":"orderBookL2_25","action":"partial","keys":["symbol","id","side"],"types":{"symbol":"symbol","id":"long","side":"symbol","size":"long","price":"float"},"foreignKeys":{"symbol":"instrument","side":"side"},"attributes":{"symbol":"parted","id":"sorted"},"filter":{"symbol":"XBTUSD"},"data":[{"symbol":"XBTUSD","id":15598960150,"side":"Sell","size":123,"price":10398.5},{"symbol":"XBTUSD","id":15598960200,"side":"Sell","size":1678,"price":10398},{"symbol":"XBTUSD","id":15598960250,"side":"Buy","size":1067,"price":10397.5},{"symbol":"XBTUSD","id":15598960300,"side":"Buy","size":30,"price":10397}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'action': "partial",
            'data': [
                {
                    "symbol": "XBTUSD",
                    "id": 15598960150,
                    "side": SELL,
                    "volume": 123,
                    "price": 10398.5
                },
                {
                    "symbol": "XBTUSD",
                    "id": 15598960200,
                    "side": SELL,
                    "volume": 1678,
                    "price": 10398
                },
                {
                    "symbol": "XBTUSD",
                    "id": 15598960250,
                    "side": BUY,
                    "volume": 1067,
                    "price": 10397.5
                },
                {
                    "symbol": "XBTUSD",
                    "id": 15598960300,
                    "side": BUY,
                    "volume": 30,
                    "price": 10397
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"update","data":[{"symbol":"XBTUSD","id":15598960150,"side":"Sell","size":1123},{"symbol":"XBTUSD","id":15598960250,"side":"Buy","size":1167}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'action': "update",
            'data': [
                {
                    "symbol": "XBTUSD",
                    "id": 15598960150,
                    "side": SELL,
                    "volume": 1123,
                },
                {
                    "symbol": "XBTUSD",
                    "id": 15598960250,
                    "side": BUY,
                    "volume": 1167,
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"delete","data":[{"symbol":"XBTUSD","id":8798661400,"side":"Sell"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'action': "delete",
            'data': [
                {
                    "symbol": "XBTUSD",
                    "id": 8798661400,
                    "side": SELL
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"insert","data":[{"symbol":"XBTUSD","id":8798623150,"side":"Sell","size":200,"price":13768.5}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'action': "insert",
            'data': [
                {
                    "symbol": "XBTUSD",
                    "id": 8798623150,
                    "side": SELL,
                    "volume": 200,
                    'price': 13768.5
                }
            ]
        }
    }
]
