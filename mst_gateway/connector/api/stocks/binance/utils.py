import hashlib
import re
from datetime import datetime
from typing import Union, Optional
from mst_gateway.connector import api
from .....exceptions import ConnectorError


def _face_price(symbol, mark_price):
    return mark_price, True


def load_symbol_data(raw_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('closeTime'))
    mark_price = to_float(raw_data.get('lastPrice'))
    face_price, _reversed = _face_price(symbol, mark_price)
    return {
        'time': symbol_time,
        'timestamp': raw_data.get('closeTime'),
        'symbol': symbol,
        'price': to_float(raw_data.get('lastPrice')),
        'price24': to_float(raw_data.get('weightedAvgPrice')),
        # 'pair': _binance_pair(symbol),
        'tick': to_float(1e-8),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed
    }


def load_exchange_symbol_info(raw_data: dict) -> dict:
    schema = []
    if raw_data.get('isSpotTradingAllowed'):
        schema.append('exchange')
    if raw_data.get('isMarginTradingAllowed'):
        schema.append('margin2')
    return {
        'symbol': raw_data.get('symbol'),
        'base_asset': raw_data.get('baseAsset'),
        'quote_asset': raw_data.get('quoteAsset'),
        'schema': schema
    }


def load_futures_exchange_symbol_info(raw_data: dict) -> dict:
    return {
        'symbol': raw_data.get('symbol'),
        'base_asset': raw_data.get('baseAsset'),
        'quote_asset': raw_data.get('quoteAsset'),
        'schema': ['futures']
    }


def _binance_pair(symbol):
    length = len(symbol)
    base = length // 2
    quote = length - base
    return symbol[:base], symbol[-quote:]


def load_trade_data(raw_data: dict, symbol: str = None) -> dict:
    """
    {
        "id": 28457,
        "price": "4.00000100",
        "qty": "12.00000000",
        "quoteQty": "48.000012",
        "time": 1499865549590,
        "isBuyerMaker": true,
        "isBestMatch": true
      }
    """
    return {
        'time': to_date(raw_data.get('time')),
        'timestamp': raw_data.get('time'),
        'symbol': symbol,
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        'side': load_order_side(raw_data.get('isBuyerMaker')),
    }


def load_order_side(order_side: bool) -> int:
    if order_side:
        return api.BUY
    return api.SELL


def load_order_book_side(order_side: str) -> int:
    if order_side == 'bids':
        return api.BUY
    return api.SELL


def generate_order_book_id(symbol: str, price: float) -> int:
    hash_object = hashlib.sha1(symbol.encode())
    res = int(re.sub(r'[^0-9.]+', r'', hash_object.hexdigest())[-15:])
    result = int(res - price * 10 ** 8)
    return result


def load_order_book_data(raw_data: dict, symbol: str, ent_side, split, offset, depth) -> Union[list, dict]:
    _raw_data = dict()
    if offset and depth:
        _raw_data['asks'] = raw_data['asks'][offset:depth + offset]
        _raw_data['bids'] = raw_data['bids'][-depth - offset:-offset]
    elif offset and depth is None:
        _raw_data['asks'] = raw_data['asks'][offset:]
        _raw_data['bids'] = raw_data['bids'][:-offset]
    elif depth:
        _raw_data['asks'] = raw_data['asks'][:depth]
        _raw_data['bids'] = raw_data['bids'][-depth:]
    else:
        _raw_data['asks'] = raw_data['asks']
        _raw_data['bids'] = raw_data['bids']
    _raw_data['asks'] = reversed(_raw_data.get('asks', []))

    res = list() if not split else dict()
    for k, v in _raw_data.items():
        side = load_order_book_side(k)
        if ent_side is not None and not ent_side == side:
            continue
        if split:
            res.update({side: list()})
            for item in v:
                res[side].append(dict(
                    id=generate_order_book_id(symbol, to_float(item[0])),
                    symbol=symbol,
                    price=to_float(item[0]),
                    volume=to_float(item[1]),
                    side=side
                ))
        else:
            for item in v:
                res.append(dict(
                    id=generate_order_book_id(symbol, to_float(item[0])),
                    symbol=symbol,
                    price=to_float(item[0]),
                    volume=to_float(item[1]),
                    side=side
                ))
    return res


def load_quote_data(raw_data: dict, symbol: str = None) -> dict:
    """
        {'id': 170622457,
        'isBestMatch': True,
        'isBuyerMaker': True,
        'price': '0.02107500',
        'qty': '17.75100000',
        'quoteQty': '0.37410232',
        'time': 1585491048725}
    """
    return {
        'time': to_date(raw_data.get('time')),
        'timestamp': raw_data.get('time'),
        'symbol': symbol,
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        'side': load_order_side(raw_data.get('isBuyerMaker')),
    }


def load_quote_bin_data(raw_data: list, symbol: str = None) -> dict:
    return {
        'time': to_date(raw_data[0]),
        'timestamp': raw_data[0],
        'symbol': symbol,
        'open': to_float(raw_data[1]),
        'close': to_float(raw_data[4]),
        'high': to_float(raw_data[2]),
        'low': to_float(raw_data[3]),
        'volume': raw_data[5],
    }


def load_order_data(raw_data: dict, skip_undef=False) -> dict:
    data = {
        'order_id': raw_data.get('orderId') or raw_data.get('clientOrderId'),
        'symbol': raw_data.get('symbol'),
        'origQty': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPrice'),
        'type': raw_data.get('type'),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'created': to_date(raw_data.get('time')),
        'active': raw_data.get('status') != "NEW",
        # 'schema': api.OrderSchema.margin1
    }
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('address')).lower()
    }
    return data


def load_spot_wallet_data(raw_data: dict) -> dict:
    return {
        'balances': _spot_balance_data(raw_data.get('balances'))
    }


def load_spot_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('balances'):
        if a.get('asset', '').upper() == asset.upper():
            return _spot_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_wallet_data(raw_data: dict) -> dict:
    return {
        'trade_enabled': raw_data.get('tradeEnabled'),
        'transfer_enabled': raw_data.get('transferEnabled'),
        'borrow_enabled': raw_data.get('borrowEnabled'),
        'margin_level': raw_data.get('marginLevel'),
        'total_balance': raw_data.get('totalAssetOfBtc'),
        'total_liability': raw_data.get('totalLiabilityOfBtc'),
        'total_net_balance': raw_data.get('totalNetAssetOfBtc'),
        'balances': _margin_balance_data(raw_data.get('userAssets'))
    }


def load_margin_wallet_detail_data(raw_data: dict, asset: str, max_borrow: dict = None) -> dict:
    for a in raw_data.get('userAssets'):
        if a.get('asset', '').upper() == asset.upper():
            return _margin_balance_data([a], _margin_max_borrow(max_borrow))[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_futures_wallet_data(raw_data: dict) -> dict:
    return {
        'trade_enabled': raw_data.get('canTrade'),
        'total_initial_margin': to_float(raw_data.get('totalInitialMargin')),
        'total_maint_margin': to_float(raw_data.get('totalMaintMargin')),
        'total_margin_balance': to_float(raw_data.get('totalMarginBalance')),
        'total_open_order_initial_margin': to_float(raw_data.get('totalOpenOrderInitialMargin')),
        'total_position_initial_margin': to_float(raw_data.get('totalPositionInitialMargin')),
        'total_unrealised_pnl': to_float(raw_data.get('totalUnrealizedProfit')),
        'total_balance': raw_data.get('totalWalletBalance'),
        'balances': _futures_balance_data(raw_data.get('assets'))
    }


def load_futures_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('assets'):
        if a.get('asset', '').upper() == asset.upper():
            return _futures_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def _spot_balance_data(balances: list):
    return [
        {
            'currency': b['asset'],
            'balance': b['free'],
            'borrowed': None,
            'available_borrow': None,
            'interest': None,
            'unrealised_pnl': 0,
            'margin_balance': to_float(b['free']),
            'maint_margin': to_float(b['locked']),
            'init_margin': None,
            'available_margin': round(to_float(b['free']) - to_float(b['locked']), 8),
            'type': to_wallet_state_type(to_float(b['locked'])),
        } for b in balances
    ]


def _margin_balance_data(balances: list, max_borrow: float = None):
    return [
        {
            'currency': b['asset'],
            'balance': b['netAsset'],
            'borrowed': b['borrowed'],
            'available_borrow': max_borrow,
            'interest': b['interest'],
            'unrealised_pnl': 0,
            'margin_balance': to_float(b['free']),
            'maint_margin': to_float(b['locked']),
            'init_margin': None,
            'available_margin': round(to_float(b['free']) - to_float(b['locked']), 8),
            'type': to_wallet_state_type(to_float(b['locked'])),
        } for b in balances
    ]


def _margin_max_borrow(data):
    if isinstance(data, dict):
        return to_float(data.get('amount'))
    return None


def _futures_balance_data(balances: list):
    return [
        {
            'currency': b['asset'],
            'balance': to_float(b['walletBalance']),
            'borrowed': None,
            'available_borrow': None,
            'interest': None,
            'unrealised_pnl': to_float(b['unrealizedProfit']),
            'margin_balance': to_float(b['marginBalance']),
            'maint_margin': to_float(b['maintMargin']),
            'init_margin': to_float(b['initialMargin']),
            'available_margin': round(to_float(b['marginBalance']) - to_float(b['maintMargin']), 8),
            'type': to_wallet_state_type(to_float(b['maintMargin'])),
        } for b in balances
    ]


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def load_transaction_id(raw_data: dict) -> dict:
    data = {
        'transaction': raw_data.get('tranId')
    }
    return data


def to_date(token: Union[datetime, int]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.fromtimestamp(token/1000)
    except ValueError:
        return None


def to_float(token: Union[int, float, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None
