from copy import deepcopy
from mst_gateway.connector.api import BUY, SELL
from mst_gateway.connector.api.stocks.bitmex.var import (
    BITMEX_BUY,
    BITMEX_SELL
)
import tests.config as cfg


TEST_ORDER_BOOK_DATA = [
    {
        "id": 8799067200,
        "symbol": "XBTUSD",
        "price": 9328.0,
        "size": 4694,
        "side": BITMEX_SELL,
        "schema": "margin1",
        "system_symbol": "btcusd"
    },
    {
        "id": 8799067250,
        "symbol": "XBTUSD",
        "price": 9327.5,
        "size": 10000,
        "side": BITMEX_SELL,
        "schema": "margin1",
        "system_symbol": "btcusd"
    },
    {
        "id": 8799067300,
        "symbol": "XBTUSD",
        "price": 9327.0,
        "size": 830005,
        "side": BITMEX_SELL,
    },
    {
        "id": 8799067350,
        "symbol": "XBTUSD",
        "price": 9326.5,
        "size": 110123,
        "side": BITMEX_SELL,
    },
    {
        "id": 8799067400,
        "symbol": "XBTUSD",
        "price": 9326.0,
        "size": 4694,
        "side": BITMEX_BUY,
    },
    {
        "id": 8799067450,
        "symbol": "XBTUSD",
        "price": 9325.5,
        "size": 84436,
        "side": BITMEX_BUY,
    },
    {
        "id": 8799067500,
        "symbol": "XBTUSD",
        "price": 9325.0,
        "size": 10000,
        "side": BITMEX_BUY,
    },
    {
        "id": 8799067550,
        "symbol": "XBTUSD",
        "price": 9324.5,
        "size": 10123,
        "side": BITMEX_BUY,
    }
]


TEST_ORDER_BOOK_STATE_DATA = {
    'system_symbol': "btcusd",
    'schema': "margin1"
}


TEST_ORDER_BOOK_SPLIT_DATA = {
    SELL: [{
        **{'volume': _v.pop('size')},
        **_v,
        **TEST_ORDER_BOOK_STATE_DATA,
        **{'side': SELL}
    } for _v in deepcopy(TEST_ORDER_BOOK_DATA[0:4])],
    BUY: [{
        **{'volume': _v.pop('size')},
        **_v,
        **TEST_ORDER_BOOK_STATE_DATA,
        **{'side': BUY}
    } for _v in deepcopy(TEST_ORDER_BOOK_DATA[4:8])],
}


TEST_ORDER_BOOK_MESSAGES = [
    {
        'message': '{"table": "orderBookL2_25", "action": "invalid"}',
        'data': None,
    },
    {
        'message': '{"table":"orderBookL2_25","action":"partial","keys":["symbol","id","side"],"types":{"symbol":"symbol","id":"long","side":"symbol","size":"long","price":"float"},"foreignKeys":{"symbol":"instrument","side":"side"},"attributes":{"symbol":"parted","id":"sorted"},"filter":{"symbol":"XBTUSD"},"data":[{"symbol":"XBTUSD","id":8799067200,"side":"Sell","size":244694,"price":9328},{"symbol":"XBTUSD","id":8799067250,"side":"Sell","size":284436,"price":9327.5},{"symbol":"XBTUSD","id":8799067300,"side":"Sell","size":830005,"price":9327},{"symbol":"XBTUSD","id":8799067350,"side":"Sell","size":110123,"price":9326.5}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "partial",
            'data': [
                {
                    "id": 8799067200,
                    "symbol": "XBTUSD",
                    "price": 9328.0,
                    "volume": 244694,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                },
                {
                    "id": 8799067250,
                    "symbol": "XBTUSD",
                    "price": 9327.5,
                    "volume": 284436,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                },
                {
                    "id": 8799067300,
                    "symbol": "XBTUSD",
                    "price": 9327.0,
                    "volume": 830005,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                },
                {
                    "id": 8799067350,
                    "symbol": "XBTUSD",
                    "price": 9326.5,
                    "volume": 110123,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"update","data":[{"symbol":"XBTUSD","id":8799068400,"side":"Sell","size":973126}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "update",
            'data': [
                {
                    "id": 8799068400,
                    "symbol": "XBTUSD",
                    "volume": 973126,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"delete","data":[{"symbol":"XBTUSD","id":8799067200,"side":"Sell"}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "delete",
            'data': [
                {
                    "id": 8799067200,
                    "symbol": "XBTUSD",
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                }
            ]
        }
    },
    {
        'message': '{"table":"orderBookL2_25","action":"insert","data":[{"symbol":"XBTUSD","id":8799068450,"side":"Sell","size":199822,"price":9315.5},{"symbol":"XBTUSD","id":8799069700,"side":"Buy","size":628292,"price":9303}]}',
        'data': {
            'account': "bitmex.test",
            'table': "order_book",
            'schema': cfg.BITMEX_SCHEMA,
            'action': "insert",
            'data': [
                {
                    "id": 8799068450,
                    "symbol": "XBTUSD",
                    "price": 9315.5,
                    "volume": 199822,
                    "side": SELL,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                },
                {
                    "id": 8799069700,
                    "symbol": "XBTUSD",
                    "price": 9303.0,
                    "volume": 628292,
                    "side": BUY,
                    "schema": "margin1",
                    "system_symbol": "btcusd"
                }
            ]
        }
    }
]
