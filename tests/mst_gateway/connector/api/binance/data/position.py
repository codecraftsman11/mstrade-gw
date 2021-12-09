from mst_gateway.connector.api.types import OrderSchema, LeverageType
from tests import config as cfg

DEFAULT_POSITIONS_STATE = {
    OrderSchema.futures: {
        'btcusdt': {
            'action': 'update',
            'cross_wallet_balance': 99760.41099324,
            'entry_price': 57000.0,
            'isolated_wallet_balance': 100000.0,
            'leverage': 1.0,
            'leverage_type': LeverageType.cross,
            'mark_price': 56900.,
            'side': 1,
            'symbol': 'btcusdt',
            'volume': 0.001,
        },
    },
    OrderSchema.futures_coin: {
        'btcusd_perp': {
            'action': 'update',
            'cross_wallet_balance': 99760.41099324,
            'entry_price': 57000.0,
            'isolated_wallet_balance': 100000.0,
            'leverage': 1.0,
            'leverage_type': LeverageType.isolated,
            'mark_price': 56900.0,
            'side': 1,
            'symbol': 'btcusd_perp',
            'volume': 0.001,
        },
    }
}


DEFAULT_POSITION_MESSAGE = {
    OrderSchema.futures: {

    },
    OrderSchema.futures_coin: {

    },
}
DEFAULT_POSITION_LOOKUP_TABLE_RESULT = {
    OrderSchema.futures: {

    },
    OrderSchema.futures_coin: {

    },
}
DEFAULT_POSITION_SPLIT_MESSAGE_RESULT = {
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
DEFAULT_POSITION_GET_DATA_RESULT = {
    OrderSchema.futures: [

    ],
    OrderSchema.futures_coin: [

    ],
}
