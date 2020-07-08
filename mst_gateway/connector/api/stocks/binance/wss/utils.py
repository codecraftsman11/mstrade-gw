import json
# from ..utils import symbol2stock
from mst_gateway.connector.api.stocks.binance.utils import to_date, to_float, load_order_side, generate_order_book_id
from mst_gateway.connector.api.stocks.bitmex.utils import calc_face_price
from mst_gateway.connector.api.utils import time2timestamp


def make_cmd(cmd, args, symbol=None):
    if symbol is not None:
        symbol = symbol
        # symbol = symbol2stock(symbol)
        args = f"{symbol}@{args}"
    if args == 'bookTicker':
        args = f'!bookTicker'
    return json.dumps({
        'method': cmd,
        'params': [args],
        'id': 1
    })


def cmd_subscribe(subscr_name, symbol=None):
    return make_cmd("SUBSCRIBE", subscr_name, symbol)


def cmd_unsubscribe(subscr_name, symbol=None):
    return make_cmd("unsubscribe", subscr_name, symbol)


def is_ok(response: str) -> bool:
    data = json.loads(response)
    return bool(data.get('success'))


def is_auth_ok(response: str) -> bool:
    data = json.loads(response)
    return not bool(data.get('error'))


def parse_message(message: str) -> dict:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        return {'raw': message}


def load_trade_ws_data(raw_data: dict, symbol: str) -> dict:
    """
    {
        "e":"trade",
        "E":1593708058756,
        "s":"BTCUSDT",
        "t":349533703,
        "p":"8958.09000000",
        "q":"0.05827000",
        "b":2606312924,
        "a":2606312902,
        "T":1593708058754,
        "m":false,
        "M":true
    }
    """
    return {
        'time': to_date(raw_data.get('E')),
        'timestamp': raw_data.get('E'),
        'symbol': symbol,
        'price': to_float(raw_data.get('p')),
        'volume': raw_data.get('q'),
        'side': load_order_side(raw_data.get('m')),
    }


def load_quote_bin_ws_data(raw_data: dict, symbol: str) -> dict:
    """
    {
      "e": "kline",     // Event type
      "E": 123456789,   // Event time
      "s": "BNBBTC",    // Symbol
      "k": {
        "t": 123400000, // Kline start time
        "T": 123460000, // Kline close time
        "s": "BNBBTC",  // Symbol
        "i": "1m",      // Interval
        "f": 100,       // First trade ID
        "L": 200,       // Last trade ID
        "o": "0.0010",  // Open price
        "c": "0.0020",  // Close price
        "h": "0.0025",  // High price
        "l": "0.0015",  // Low price
        "v": "1000",    // Base asset volume
        "n": 100,       // Number of trades
        "x": false,     // Is this kline closed?
        "q": "1.0000",  // Quote asset volume
        "V": "500",     // Taker buy base asset volume
        "Q": "0.500",   // Taker buy quote asset volume
        "B": "123456"   // Ignore
      }
    }
    """
    quote_time = to_date(raw_data.get('E'))
    return {
        'time': quote_time,
        'timestamp': time2timestamp(quote_time),
        'symbol': symbol,
        'schema': None,
        'open': to_float(raw_data.get('k', {}).get("o")),
        'close': to_float(raw_data.get('k', {}).get("c")),
        'high': to_float(raw_data.get('k', {}).get("h")),
        'low': to_float(raw_data.get('k', {}).get('l')),
        'volume': raw_data.get('k', {}).get('v'),
    }


def load_order_book_ws_data(raw_data: dict, order: list, side: int) -> dict:
    """
    {
      "e": "depthUpdate",
      "E": 1594200464954,
      "s": "BTCUSDT",
      "U": 4862390979,
      "u": 4862391096,
      "b": [
        [
          "9270.04000000",
          "0.00000000"
        ],
        [
          "9270.03000000",
          "0.00000000"
        ]
      ],
      "a": [
        [
          "9270.01000000",
          "1.26026600"
        ],
        [
          "9270.02000000",
          "0.00000000"
        ]
      ]
    }
    """
    symbol = raw_data.get('s', '').lower()
    price = to_float(order[0])

    return {
        'id': generate_order_book_id(symbol, price),
        'symbol': symbol,
        'price': price,
        'volume': to_float(order[1]),
        'side': side
    }


def load_symbol_ws_data(raw_data: dict) -> dict:
    """
    {
      "e": "24hrTicker",  // Event type
      "E": 123456789,     // Event time
      "s": "BNBBTC",      // Symbol
      "p": "0.0015",      // Price change
      "P": "250.00",      // Price change percent
      "w": "0.0018",      // Weighted average price
      "x": "0.0009",      // First trade(F)-1 price (first trade before the 24hr rolling window)
      "c": "0.0025",      // Last price
      "Q": "10",          // Last quantity
      "b": "0.0024",      // Best bid price
      "B": "10",          // Best bid quantity
      "a": "0.0026",      // Best ask price
      "A": "100",         // Best ask quantity
      "o": "0.0010",      // Open price
      "h": "0.0025",      // High price
      "l": "0.0010",      // Low price
      "v": "10000",       // Total traded base asset volume
      "q": "18",          // Total traded quote asset volume
      "O": 0,             // Statistics open time
      "C": 86400000,      // Statistics close time
      "F": 0,             // First trade ID
      "L": 18150,         // Last trade Id
      "n": 18151          // Total number of trades
    }
    """
    symbol = raw_data.get('s')
    symbol_time = to_date(raw_data.get('E'))
    mark_price = to_float(raw_data.get('o'))
    face_price, _reversed = calc_face_price(symbol, mark_price)
    return {
        'time': symbol_time,
        'timestamp': time2timestamp(symbol_time),
        'symbol': symbol,
        'price': to_float(raw_data.get('c')),
        'price24': to_float(raw_data.get('w')),
        # 'pair': _get_symbol_pair(raw_data.get('symbol'),
        #                          raw_data.get('rootSymbol')),
        'tick': None,
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('b')),
        'ask_price': to_float(raw_data.get('a')),
        'reversed': _reversed
    }
