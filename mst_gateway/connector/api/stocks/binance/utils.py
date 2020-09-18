import hashlib
import re
from datetime import datetime
from typing import Union, Optional
from mst_gateway.connector import api
from mst_gateway.calculator.binance import BinanceFinFactory
from mst_gateway.connector.api.types.order import OrderSchema
from .....exceptions import ConnectorError
from . import var


def _face_price(symbol, mark_price):
    return mark_price, True


def load_symbol_data(raw_data: dict, state_data: dict) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('closeTime'))
    mark_price = to_float(raw_data.get('lastPrice'))
    face_price, _reversed = _face_price(symbol, mark_price)
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('weightedAvgPrice'))
    return {
        'time': symbol_time,
        'timestamp': raw_data.get('closeTime'),
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': symbol_delta(price, price24),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice') or mark_price),
        'ask_price': to_float(raw_data.get('askPrice') or mark_price),
        'reversed': _reversed,
        'volume24': to_float(raw_data.get('volume')),
        'expiration': state_data.get('expiration'),
        'pair': state_data.get('pair'),
        'tick': state_data.get('tick'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'symbol_schema': state_data.get('symbol_schema'),
    }


def load_exchange_symbol_info(raw_data: list) -> list:
    symbol_list = []
    for d in raw_data:
        if d.get('status') == 'TRADING':
            if d.get('isSpotTradingAllowed'):
                symbol_list.append(
                    {
                        'symbol': d.get('symbol'),
                        'base_asset': d.get('baseAsset'),
                        'quote_asset': d.get('quoteAsset'),
                        'expiration': None,
                        'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                        'schema': OrderSchema.exchange,
                        'symbol_schema': OrderSchema.exchange,
                        'tick': to_float(d.get('filters', [{}])[0].get('tickSize'))
                    }
                )
            if d.get('isMarginTradingAllowed'):
                symbol_list.append(
                    {
                        'symbol': d.get('symbol'),
                        'base_asset': d.get('baseAsset'),
                        'quote_asset': d.get('quoteAsset'),
                        'expiration': None,
                        'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                        'schema': OrderSchema.margin2,
                        'symbol_schema': OrderSchema.margin2,
                        'tick': to_float(d.get('filters', [{}])[0].get('tickSize'))
                    }
                )
    return symbol_list


def load_futures_exchange_symbol_info(raw_data: list) -> list:
    symbol_list = []
    for d in raw_data:
        if d.get('status') == 'TRADING':
            symbol_list.append(
                {
                    'symbol': d.get('symbol'),
                    'base_asset': d.get('baseAsset'),
                    'quote_asset': d.get('quoteAsset'),
                    'expiration': None,
                    'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                    'schema': OrderSchema.futures,
                    'symbol_schema': OrderSchema.futures,
                    'tick': to_float(d.get('filters', [{}])[0].get('tickSize'))
                }
            )
    return symbol_list


def _binance_pair(symbol):
    length = len(symbol)
    base = length // 2
    quote = length - base
    return symbol[:base], symbol[-quote:]


def load_trade_data(raw_data: dict, state_data: dict) -> dict:
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
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        'side': load_order_side(raw_data.get('isBuyerMaker')),
        'symbol': state_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
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


def filter_order_book_data(data: dict, min_volume_buy: float = None, min_volume_sell: float = None) -> dict:
    if min_volume_buy is not None and min_volume_sell is not None:
        data['bids'] = [bid for bid in data.get('bids', []) if to_float(bid[1]) >= min_volume_buy]
        data['asks'] = [ask for ask in data.get('asks', []) if to_float(ask[1]) >= min_volume_sell]
    elif min_volume_buy is not None:
        data['bids'] = [bid for bid in data.get('bids', []) if to_float(bid[1]) >= min_volume_buy]
    elif min_volume_sell is not None:
        data['asks'] = [ask for ask in data.get('asks', []) if to_float(ask[1]) >= min_volume_sell]
    return data


def load_order_book_data(raw_data: dict, symbol: str, side, split,
                         offset, depth, state_data: dict) -> Union[list, dict]:
    _raw_data = dict()
    if offset and depth:
        _raw_data['asks'] = raw_data['asks'][offset:depth + offset]
        _raw_data['bids'] = raw_data['bids'][offset:depth + offset]
    elif offset and depth is None:
        _raw_data['asks'] = raw_data['asks'][offset:]
        _raw_data['bids'] = raw_data['bids'][offset:]
    elif depth:
        _raw_data['asks'] = raw_data['asks'][:depth]
        _raw_data['bids'] = raw_data['bids'][:depth]
    else:
        _raw_data['asks'] = raw_data['asks']
        _raw_data['bids'] = raw_data['bids']
    _raw_data['asks'] = reversed(_raw_data.get('asks', []))

    resp = list() if not split else dict()
    for k, v in _raw_data.items():
        _side = load_order_book_side(k)
        if side is not None and not side == _side:
            continue
        if split:
            resp.update({_side: list()})
            for item in v:
                resp[_side].append(dict(
                    id=generate_order_book_id(symbol, to_float(item[0])),
                    symbol=symbol,
                    price=to_float(item[0]),
                    volume=to_float(item[1]),
                    side=_side,
                    schema=state_data.get('schema'),
                    system_symbol=state_data.get('system_symbol'),
                ))
        else:
            for item in v:
                resp.append(dict(
                    id=generate_order_book_id(symbol, to_float(item[0])),
                    symbol=symbol,
                    price=to_float(item[0]),
                    volume=to_float(item[1]),
                    side=_side,
                    schema=state_data.get('schema'),
                    system_symbol=state_data.get('system_symbol'),
                ))
    return resp


def load_quote_data(raw_data: dict, state_data: dict) -> dict:
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
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        'side': load_order_side(raw_data.get('isBuyerMaker')),
        'symbol': state_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
    }


def load_quote_bin_data(raw_data: list, state_data: dict) -> dict:
    return {
        'time': to_date(raw_data[0]),
        'timestamp': raw_data[0],
        'open': to_float(raw_data[1]),
        'close': to_float(raw_data[4]),
        'high': to_float(raw_data[2]),
        'low': to_float(raw_data[3]),
        'volume': raw_data[5],
        'symbol': state_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
    }


def load_order_data(raw_data: dict, state_data: dict) -> dict:
    order_type_and_exec = var.BINANCE_ORDER_TYPE_AND_EXECUTION_MAP.get(
        raw_data.get('type', '').upper()
    ) or {'type': None, 'execution': None}
    data = {
        'order_id': raw_data.get('orderId') or raw_data.get('clientOrderId'),
        'symbol': raw_data.get('symbol'),
        'origQty': raw_data.get('orderQty'),
        'stop': raw_data.get('stopPrice'),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'created': to_date(raw_data.get('time')),
        'active': raw_data.get('status') != "NEW",
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        **order_type_and_exec,
    }
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('address')).lower()
    }
    return data


def load_spot_wallet_data(raw_data: dict, currencies: dict,
                          assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = _spot_balance_data(raw_data.get('balances'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def load_spot_wallet_balances(raw_data: dict) -> list:
    return _spot_balance_data(raw_data.get('balances'))


def load_spot_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    if not raw_data.get('balances'):
        return _mock_balance_data(asset)
    for a in raw_data.get('balances'):
        if a.get('asset', '').upper() == asset.upper():
            return _spot_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_wallet_data(raw_data: dict, currencies: dict,
                            assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = _margin_balance_data(raw_data.get('userAssets'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        'trade_enabled': raw_data.get('tradeEnabled'),
        'transfer_enabled': raw_data.get('transferEnabled'),
        'borrow_enabled': raw_data.get('borrowEnabled'),
        'margin_level': raw_data.get('marginLevel'),
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
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


def load_futures_wallet_data(raw_data: dict, currencies: dict,
                             assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = _futures_balance_data(raw_data.get('assets'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        'trade_enabled': raw_data.get('canTrade'),
        'total_initial_margin': to_float(raw_data.get('totalInitialMargin')),
        'total_maint_margin': to_float(raw_data.get('totalMaintMargin')),
        'total_open_order_initial_margin': to_float(raw_data.get('totalOpenOrderInitialMargin')),
        'total_position_initial_margin': to_float(raw_data.get('totalPositionInitialMargin')),
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def load_future_wallet_balances(raw_data: dict) -> list:
    return _futures_balance_data(raw_data.get('assets'))


def load_futures_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('assets'):
        if a.get('asset', '').upper() == asset.upper():
            return _futures_balance_data([a])[0]
    raise ConnectorError(f"Invalid asset {asset}.")


def ws_spot_wallet(**kwargs):
    assets = kwargs.get('assets', ('btc', 'usd'))
    fields = ('balance',)
    data = kwargs.get('item', dict())
    currencies = dict()
    return _ws_load_spot_wallet_data(data, currencies, assets, fields)


def _ws_load_spot_wallet_data(raw_data: dict, currencies: dict,
                              assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = ws_spot_balance_data(raw_data.get('B'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        **_load_total_wallet_summary_list(total_balance, fields),
        'balances': balances
    }


def ws_spot_balance_data(balances: list):
    return [
        {
            'currency': b['a'],
            'balance': to_float(b['f']),
            'unrealised_pnl': 0,
            'margin_balance': to_float(b['f']),
            'maint_margin': to_float(b['l']),
            'init_margin': None,
            'available_margin': round(to_float(b['f']) - to_float(b['l']), 8),
            'type': to_wallet_state_type(to_float(b['l'])),
        } for b in balances
    ]


def ws_margin_wallet(**kwargs):
    assets = kwargs.get('assets', ('btc', 'usd'))
    fields = ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed')
    data = kwargs.get('item', dict())
    currencies = dict()
    return _ws_load_margin_wallet_data(data, currencies, assets, fields)


def _ws_load_margin_wallet_data(raw_data: dict, currencies: dict,
                                assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = ws_margin_balance_data(raw_data.get('B'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        'trade_enabled': raw_data.get('T'),
        'transfer_enabled': raw_data.get('W'),
        'borrow_enabled': True,  # mock data
        'margin_level': 999,  # mock data
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def ws_margin_balance_data(balances: list):
    return [
        {
            'currency': b['a'],
            'balance': to_float(b['f']),
            'unrealised_pnl': 0,
            'margin_balance': to_float(b['f']),  # mock data
            'maint_margin': to_float(b['l']),  # mock data
            'init_margin': None,
            'available_margin': round(to_float(b['f']) - to_float(b['l']), 8),
            'type': to_wallet_state_type(to_float(b['l'])),
            'borrowed': 0,  # mock data
            'interest': 0.0008333,  # mock data
        } for b in balances
    ]


def ws_futures_wallet(**kwargs):
    assets = kwargs.get('assets', ('btc', 'usd'))
    fields = ('balance', 'unrealised_pnl', 'margin_balance')
    data = kwargs.get('item', dict())
    currencies = dict()
    return _ws_load_futures_wallet_data(data, currencies, assets, fields)


def _ws_load_futures_wallet_data(raw_data: dict, currencies: dict,
                                 assets: Union[list, tuple], fields: Union[list, tuple]) -> dict:
    balances = ws_futures_balance_data(raw_data.get('a', {}).get('B'), raw_data.get('a', {}).get('P'))
    total_balance = dict()
    for asset in assets:
        total_balance[asset] = load_wallet_summary(currencies, balances, asset, fields)
    return {
        'trade_enabled': True,  # mock data
        'total_initial_margin': 0,  # mock data
        'total_maint_margin': 0,  # mock data
        'total_open_order_initial_margin': 0,  # mock data
        'total_position_initial_margin': 0,  # mock data
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def ws_futures_balance_data(balances: list, position: list):
    unrealised_pnl = sum([to_float(p['up']) for p in position]) if position else 0
    return [
        {
            'currency': b['a'],
            'balance': to_float(b['wb']),
            'unrealised_pnl': unrealised_pnl,
            'margin_balance': to_float(b['wb']) + unrealised_pnl,
            'maint_margin': 0,  # mock data
            'init_margin': 0,  # mock data
            'available_margin': to_float(b['wb']) + unrealised_pnl - 0,  # mock data
            'type': to_wallet_state_type(position),
            'borrowed': None,
            'interest': None,
        } for b in balances
    ]


def _mock_balance_data(asset) -> dict:
    return {
        'currency': asset.upper(),
        'balance': 0,
        'withdraw_balance': 0,
        'borrowed': 0,
        'available_borrow': 0,
        'interest': 0,
        'interest_rate': 0,
        'unrealised_pnl': 0,
        'margin_balance': 0,
        'maint_margin': 0,
        'init_margin': 0,
        'available_margin': 0,
        'type': to_wallet_state_type(0),
    }


def _spot_balance_data(balances: list):
    return [
        {
            'currency': b['asset'],
            'balance': to_float(b['free']),
            'withdraw_balance': to_float(b['free']),
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
            'withdraw_balance': to_float(b['netAsset']),
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
            'balance': to_float(b['walletBalance']),
            'withdraw_balance': to_float(b['maxWithdrawAmount']),
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


def _load_total_wallet_summary_list(summary, fields):
    total = dict()
    for field in fields:
        t_field = f'total_{field}'
        total[t_field] = dict()
        for k, v in summary.items():
            if total[t_field].get(k):
                total[t_field][k] += v[field]
            else:
                total[t_field][k] = v[field]
    for f, asset in total.items():
        for k, v in asset.items():
            total[f][k] = round(v, 8)
    return total


def load_wallet_summary(currencies: dict, balances: list, asset: str,
                        fields: Union[list, tuple, None]):
    if fields is None:
        fields = ('balance',)
    if asset.lower() == 'usd':
        asset = 'usdt'
    total_balance = dict()
    for f in fields:
        total_balance[f] = 0
    _asset_price = (currencies.get(f"{asset}usdt".lower()) or 1)
    for b in balances:
        if b['currency'].lower() == asset.lower() or b['currency'].lower() == 'usdt':
            _price = 1
        else:
            _price = currencies.get(f"{b['currency']}usdt".lower()) or 0
        for f in fields:
            total_balance[f] += _price * (b[f] or 0) / _asset_price
    return total_balance


def load_currencies_as_dict(currencies: list):
    return {cur['symbol'].lower(): to_float(cur['price']) for cur in currencies}


def load_currencies_as_list(currencies: list):
    return [{cur['symbol'].lower(): to_float(cur['price'])} for cur in currencies]


def load_total_wallet_summary(total: dict, summary: dict, assets: Union[list, tuple], fields: Union[list, tuple]):
    for schema in summary.keys():
        for field in fields:
            t_field = f'total_{field}'
            if total.get(t_field) is None:
                total[t_field] = dict()
            for asset in assets:
                if total[t_field].get(asset) is None:
                    total[t_field][asset] = summary[schema][asset][field]
                else:
                    total[t_field][asset] += summary[schema][asset][field]
    return total


def load_currency_exchange_symbol(currency: Union[list, dict]) -> list:
    if isinstance(currency, dict):
        currency = [currency]
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('price'))} for c in currency]


def load_symbols_currencies(currency: list) -> dict:
    return {c.get('symbol', '').lower(): to_float(c.get('price')) for c in currency}


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def load_transaction_id(raw_data: dict) -> dict:
    data = {
        'transaction': raw_data.get('tranId')
    }
    return data


def load_commission(commissions: dict, currency: str, fee_tier) -> dict:
    commission = dict()
    for _c in commissions:
        if fee_tier == str(_c.get('level')):
            commission = _c
            break

    maker = to_float(commission.get('makerCommission'))
    taker = to_float(commission.get('takerCommission'))
    return dict(
        currency=currency.lower(),
        maker=maker,
        taker=taker,
        type=f"VIP{fee_tier}"
    )


def load_trade_ws_data(raw_data: dict, state_data: dict) -> dict:
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
        'price': to_float(raw_data.get('p')),
        'volume': to_float(raw_data.get('q')),
        'side': load_order_side(raw_data.get('m')),
        'symbol': state_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
    }


def load_quote_bin_ws_data(raw_data: dict, state_data: dict) -> dict:
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
    return {
        'time': to_date(raw_data.get('E')),
        'timestamp': raw_data.get('E'),
        'open': to_float(raw_data.get('k', {}).get("o")),
        'close': to_float(raw_data.get('k', {}).get("c")),
        'high': to_float(raw_data.get('k', {}).get("h")),
        'low': to_float(raw_data.get('k', {}).get('l')),
        'volume': to_float(raw_data.get('k', {}).get('v')),
        'symbol': state_data.get('symbol'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
    }


def load_order_book_ws_data(raw_data: dict, order: list, side: int, state_data: dict) -> dict:
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
        'side': side,
        'schema': state_data.get('schema'),
        'system_symbol': state_data.get('system_symbol')
    }


def load_symbol_ws_data(raw_data: dict, state_data: dict) -> dict:
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
    mark_price = to_float(raw_data.get('o'))
    face_price, _reversed = BinanceFinFactory.calc_face_price(symbol, mark_price)
    price = to_float(raw_data.get('c'))
    price24 = to_float(raw_data.get('w'))
    return {
        'time': to_date(raw_data.get('E')),
        'timestamp': raw_data.get('E'),
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': symbol_delta(price, price24),
        'mark_price': mark_price,
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('b') or mark_price),
        'ask_price': to_float(raw_data.get('a') or mark_price),
        'reversed': _reversed,
        'expiration': state_data.get('expiration'),
        'pair': state_data.get('pair'),
        'tick': state_data.get('tick'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        'symbol_schema': state_data.get('symbol_schema'),
    }


def symbol_delta(price, price24):
    if price and price24:
        return round((price - price24) / price24 * 100, 2)
    return 100


def to_date(token: Union[datetime, int]) -> Optional[datetime]:
    if isinstance(token, datetime):
        return token
    try:
        return datetime.fromtimestamp(token/1000)
    except (ValueError, TypeError):
        return None


def to_float(token: Union[int, float, str, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return None


def symbol2stock(symbol):
    return symbol.upper() if isinstance(symbol, str) else None


def stock2symbol(symbol):
    return symbol.lower() if isinstance(symbol, str) else None


def load_ws_order_side(order_side: Optional[str]) -> Optional[int]:
    if order_side == var.BINANCE_ORDER_SIDE_BUY:
        return api.BUY
    elif order_side == var.BINANCE_ORDER_SIDE_SELL:
        return api.SELL
    else:
        return None


def load_order_ws_data(raw_data: dict, state_data: dict) -> dict:
    order_type_and_exec = var.BINANCE_ORDER_TYPE_AND_EXECUTION_MAP.get(
        raw_data.get('o', '').upper()
    ) or {'type': None, 'execution': None}
    data = {
        'order_id': raw_data.get('c'),
        'symbol': raw_data.get('s'),
        'value': to_float(raw_data.get('q')),
        'stop': to_float(raw_data['P']) if raw_data.get('P') else to_float(raw_data.get('sp')),
        'side': load_ws_order_side(raw_data.get('S')),
        'price': to_float(raw_data.get('p')),
        'created': to_date(raw_data['O']) if raw_data.get('O') else to_date(raw_data.get('T')),
        'active': raw_data.get('X') != var.BINANCE_ORDER_STATUS_NEW,
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema'),
        **order_type_and_exec,
    }
    return data


def load_ws_execution_status(binance_order_status: Optional[str]) -> Optional[str]:
    return var.BINANCE_EXECUTION_STATUS_MAP.get(binance_order_status)


def calculate_ws_execution_leaves_volume(raw_data: dict) -> Optional[float]:
    return to_float(raw_data['q']) - to_float(raw_data['z']) if raw_data.get('q') and raw_data.get('z') else 0.0


def calculate_ws_execution_avg_price(raw_data: dict) -> Optional[float]:
    if raw_data.get('ap'):
        return to_float(raw_data['ap'])
    elif raw_data.get('Z') and raw_data.get('z') and to_float(raw_data['z']):
        return to_float(raw_data['Z'])/to_float(raw_data['z'])
    else:
        return 0.0


def load_execution_ws_data(message_data: dict, raw_data: dict, state_data: dict) -> Optional[dict]:
    return {
        'order_id': raw_data.get('c'),
        'side': load_ws_order_side(raw_data.get('S')),
        'tick_volume': to_float(raw_data.get('l')),
        'tick_price': to_float(raw_data.get('L')),
        'volume': to_float(raw_data.get('q')),
        'price': to_float(raw_data.get('p')),
        'type': raw_data['x'].lower() if raw_data.get('x') else None,
        'status': load_ws_execution_status(raw_data.get('X')),
        'is_active': raw_data.get('X') != var.BINANCE_ORDER_STATUS_NEW,
        'leaves_volume': calculate_ws_execution_leaves_volume(raw_data),
        'filled_volume': to_float(raw_data.get('z')),
        'avg_price': calculate_ws_execution_avg_price(raw_data),
        'timestamp': to_date(message_data.get('E')) if message_data != raw_data else to_date(raw_data.get('E')),
        'symbol': raw_data.get('s'),
        'system_symbol': state_data.get('system_symbol'),
        'schema': state_data.get('schema')
    }
