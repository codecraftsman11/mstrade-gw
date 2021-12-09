from mst_gateway.connector.api.types import OrderSchema

DEFAULT_QUOTE_BIN_MESSAGE = {
    OrderSchema.exchange: {'e': 'kline', 'E': 1638966077539, 's': 'BTCUSDT',
                           'k': {'t': 1638966060000, 'T': 1638966119999, 's': 'BTCUSDT', 'i': '1m', 'f': 468151,
                                 'L': 468160, 'o': '49071.80000000', 'c': '49063.85000000', 'h': '49071.80000000',
                                 'l': '49056.95000000', 'v': '0.06514700', 'n': 10, 'x': False, 'q': '3196.33704025',
                                 'V': '0.06314700', 'Q': '3098.20176025', 'B': '0'}},
    OrderSchema.futures: {'e': 'kline', 'E': 1638966178990, 's': 'BTCUSDT',
                          'k': {'t': 1638966120000, 'T': 1638966179999, 's': 'BTCUSDT', 'i': '1m', 'f': 217098550,
                                'L': 217098713, 'o': '49066.29', 'c': '48946.70', 'h': '49068.26', 'l': '48929.80',
                                'v': '3113.884', 'n': 164, 'x': False, 'q': '152555614.92275', 'V': '457.601',
                                'Q': '22407682.81888', 'B': '0'}},
    OrderSchema.futures_coin: {'e': 'kline', 'E': 1638966273261, 's': "BTCUSD_PERP",
                               'k': {'t': 1638966240000, 'T': 1638966299999, 's': "BTCUSD_PERP", 'i': '1m',
                                     'f': 50099279, 'L': 50099378, 'o': '48946.7', 'c': '48857.5', 'h': '48960.8',
                                     'l': '48857.5', 'v': '489', 'n': 100, 'x': False, 'q': '0.99949540', 'V': '71',
                                     'Q': '0.14504390', 'B': '0'}},
}
DEFAULT_QUOTE_BIN_LOOKUP_TABLE_RESULT = {
    OrderSchema.exchange: {

    },
    OrderSchema.futures: {

    },
    OrderSchema.futures_coin: {

    },
}
DEFAULT_QUOTE_BIN_SPLIT_MESSAGE_RESULT = {
    OrderSchema.exchange: [

    ],
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
DEFAULT_QUOTE_BIN_GET_DATA_RESULT = {
    OrderSchema.exchange: [

    ],
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
