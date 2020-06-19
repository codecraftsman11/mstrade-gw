import hashlib
import re
from datetime import datetime
from typing import Union, Optional, Tuple
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
        'pair': _binance_pair(symbol),
        'tick': to_float(1e-8),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed
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


def load_spot_wallet_data(raw_data: dict, currencies: dict) -> dict:
    balances = _spot_balance_data(raw_data.get('balances'))
    total_balance_btc = load_wallet_summary(currencies, balances, 'btc', ['balance'])
    total_balance_usd = load_wallet_summary(currencies, balances, 'usdt', ['balance'])
    return {
        'total_balance_btc': round(total_balance_btc['balance'], 8),
        'total_balance_usd': round(total_balance_usd['balance'], 8),
        'balances': balances
    }


def load_spot_wallet_balances(raw_data: dict) -> list:
    return _spot_balance_data(raw_data.get('balances'))


def load_spot_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('balances'):
        if a.get('asset', '').upper() == asset.upper():
            return _spot_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_wallet_data(raw_data: dict, currencies: dict) -> dict:
    balances = _margin_balance_data(raw_data.get('userAssets'))
    total_balance_btc = load_wallet_summary(currencies, balances, 'btc', ['balance', 'borrowed', 'margin_balance'])
    total_balance_usd = load_wallet_summary(currencies, balances, 'usdt', ['balance', 'borrowed', 'margin_balance'])
    return {
        'total_balance_btc': round(total_balance_btc['balance'], 8),
        'total_balance_usd': round(total_balance_usd['balance'], 8),
        'total_borrowed_btc': round(total_balance_btc['borrowed'], 8),
        'total_borrowed_usd': round(total_balance_usd['borrowed'], 8),
        'total_margin_balance_btc': round(total_balance_btc['margin_balance'], 8),
        'total_margin_balance_usd': round(total_balance_usd['margin_balance'], 8),
        'trade_enabled': raw_data.get('tradeEnabled'),
        'transfer_enabled': raw_data.get('transferEnabled'),
        'borrow_enabled': raw_data.get('borrowEnabled'),
        'margin_level': raw_data.get('marginLevel'),
        'balances': balances
    }


def load_margin_wallet_balances(raw_data: dict) -> list:
    return _margin_balance_data(raw_data.get('userAssets'))


def load_margin_wallet_detail_data(raw_data: dict, asset: str,
                                   max_borrow: dict, interest_rate: float) -> dict:
    for a in raw_data.get('userAssets'):
        if a.get('asset', '').upper() == asset.upper():
            return _margin_balance_data(
                balances=[a],
                max_borrow=_margin_max_borrow(max_borrow),
                interest_rate=interest_rate
            )[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def get_vip(data: dict) -> str:
    return str(data.get('feeTier', 0))


def get_interest_rate(asset_rates: list, vip_level: str, asset: str):
    _h1_rate = None
    for rate in asset_rates:
        if rate.get('assetName', '').upper() == asset.upper():
            for spec in rate['specs']:
                if str(spec.get('vipLevel')) == vip_level:
                    _r = to_float(spec.get('dailyInterestRate')) or 0
                    _h1_rate = round(_r * 100 / 24, 8)
                    break
    return _h1_rate


def load_futures_wallet_data(raw_data: dict, currencies: dict) -> dict:
    balances = _futures_balance_data(raw_data.get('assets'))
    total_balance_btc = load_wallet_summary(currencies, balances, 'btc', ['balance', 'margin_balance'])
    total_balance_usd = load_wallet_summary(currencies, balances, 'usdt', ['balance', 'margin_balance'])
    return {
        'total_balance_btc': round(total_balance_btc['balance'], 8),
        'total_balance_usd': round(total_balance_usd['balance'], 8),
        'total_margin_balance_btc': round(total_balance_btc['margin_balance'], 8),
        'total_margin_balance_usd': round(total_balance_usd['margin_balance'], 8),
        'trade_enabled': raw_data.get('canTrade'),
        'total_initial_margin': to_float(raw_data.get('totalInitialMargin')),
        'total_maint_margin': to_float(raw_data.get('totalMaintMargin')),
        'total_open_order_initial_margin': to_float(raw_data.get('totalOpenOrderInitialMargin')),
        'total_position_initial_margin': to_float(raw_data.get('totalPositionInitialMargin')),
        'total_unrealised_pnl': to_float(raw_data.get('totalUnrealizedProfit')),
        'balances': balances
    }


def load_future_wallet_balances(raw_data: dict) -> list:
    return _futures_balance_data(raw_data.get('assets'))


def load_futures_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('assets'):
        if a.get('asset', '').upper() == asset.upper():
            return _futures_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def _spot_balance_data(balances: list):
    return [
        {
            'currency': b['asset'],
            'balance': to_float(b['free']),
            'borrowed': None,
            'available_borrow': None,
            'interest': None,
            'interest_rate': None,
            'unrealised_pnl': 0,
            'margin_balance': to_float(b['free']),
            'maint_margin': to_float(b['locked']),
            'init_margin': None,
            'available_margin': round(to_float(b['free']) - to_float(b['locked']), 8),
            'type': to_wallet_state_type(to_float(b['locked'])),
        } for b in balances
    ]


def _margin_balance_data(balances: list, max_borrow: float = None, interest_rate: float = None):
    return [
        {
            'currency': b['asset'],
            'balance': to_float(b['netAsset']),
            'borrowed': to_float(b['borrowed']),
            'available_borrow': max_borrow,
            'interest': to_float(b['interest']),
            'interest_rate': interest_rate,
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
            'balance': to_float(b['maxWithdrawAmount']),
            'borrowed': None,
            'available_borrow': None,
            'interest': None,
            'interest_rate': None,
            'unrealised_pnl': abs(to_float(b['unrealizedProfit'])),
            'margin_balance': to_float(b['marginBalance']),
            'maint_margin': to_float(b['maintMargin']),
            'init_margin': to_float(b['initialMargin']),
            'available_margin': round(to_float(b['marginBalance']) - to_float(b['maintMargin']), 8),
            'type': to_wallet_state_type(to_float(b['maintMargin'])),
        } for b in balances
    ]


def load_wallet_summary(currencies: dict, balances: list, asset: str,
                        fields: Union[list, tuple, None]):
    if fields is None:
        fields = ('balance',)
    total_balance = dict()
    for f in fields:
        total_balance[f] = 0
    for b in balances:
        if b['currency'].lower() == asset.lower():
            _price = 1
        else:
            _price = currencies.get(f"{b['currency']}{asset}".lower()) or 0
        for f in fields:
            total_balance[f] += _price * (b[f] or 0)
    return total_balance


def load_currencies_as_dict(currencies: list):
    return {cur['symbol'].lower(): to_float(cur['price']) for cur in currencies}


def load_currencies_as_list(currencies: list):
    return [{cur['symbol'].lower(): to_float(cur['price'])} for cur in currencies]


def load_total_wallet_summary(total: dict, summary: dict, asset: str, fields: Union[list, tuple]):
    for f in fields:
        if total.get(f'total_{f}_{asset}'):
            total[f'total_{f}_{asset}'] += summary[f]
        else:
            total[f'total_{f}_{asset}'] = summary[f]
    return total


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('price'))} for c in currency]


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


def to_float(token: Union[int, float, str, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None
