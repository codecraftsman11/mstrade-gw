import re
from typing import Dict, Union, Optional, Tuple
from datetime import datetime, timedelta
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector import api
from mst_gateway.exceptions import ConnectorError
from mst_gateway.connector.api.types.order import LeverageType, OrderSchema, PositionSide
from mst_gateway.utils import delta
from . import var
from .converter import BitmexOrderTypeConverter
from ...types.asset import to_system_asset
from ...types.binsize import BinSize
from ...utils.order_book import generate_order_book_id


def load_symbol_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('timestamp'))
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    data = {
        'time': symbol_time,
        'symbol': symbol,
        'price': price,
        'price24': price24,
        'delta': delta(price, price24),
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'volume24': raw_data.get('volume24h'),
        'mark_price': raw_data.get('markPrice'),
        'high_price': to_float(raw_data.get('highPrice')),
        'low_price': to_float(raw_data.get('lowPrice')),
        'funding_rate': load_funding_rate(raw_data.get('fundingRate'))
    }
    if isinstance(state_data, dict):
        face_price = None
        if face_price_data := state_data.get('extra', {}).get('face_price_data', {}):
            face_price = BitmexFinFactory.calc_face_price(price, **face_price_data)
        data.update({
            'expiration': state_data.get('expiration'),
            'expiration_date': state_data.get('expiration_date'),
            'pair': state_data.get('pair'),
            'tick': state_data.get('tick'),
            'volume_tick': state_data.get('volume_tick'),
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema'),
            'created': to_date(state_data.get('created')),
            'max_leverage': state_data.get('max_leverage'),
            'wallet_asset': state_data.get('wallet_asset'),
            'face_price': face_price,
        })
    return data


def load_symbol_ws_data(raw_data: dict, state_data: Optional[dict], use_state: bool = False) -> dict:
    symbol = raw_data.get('symbol')
    symbol_time = to_iso_datetime(raw_data.get('timestamp'))
    price = to_float(raw_data.get('lastPrice'))
    price24 = to_float(raw_data.get('prevPrice24h'))
    funding_rate = to_float(raw_data.get('fundingRate'))
    if not use_state:
        funding_rate = load_funding_rate(funding_rate)
    data = {
        'tm': symbol_time,
        's': symbol,
        'p': price,
        'p24': price24,
        'dt': delta(price, price24),
        'bip': to_float(raw_data.get('bidPrice')),
        'asp': to_float(raw_data.get('askPrice')),
        'v24': raw_data.get('volume24h'),
        'mp': to_float(raw_data.get('markPrice')),
        'hip': to_float(raw_data.get("highPrice")),
        'lop': to_float(raw_data.get('lowPrice')),
        'fr': funding_rate
    }
    if isinstance(state_data, dict):
        face_price_data = state_data.get('extra', {}).get('face_price_data', {})
        face_price = BitmexFinFactory.calc_face_price(price, **face_price_data)
        data.update({
            'fp': face_price,
            'exp': state_data.get('expiration'),
            'expd': state_data.get('expiration_date'),
            'pa': state_data.get('pair'),
            'tck': state_data.get('tick'),
            'vt': state_data.get('volume_tick'),
            'ss': state_data.get('system_symbol'),
            'crt': to_iso_datetime(state_data.get('created')),
            'mlvr': state_data.get('max_leverage'),
            'wa': state_data.get('wallet_asset'),
        })
    return data


def load_funding_rate(value: float) -> float:
    return value * 100 if value else value


def load_currency_exchange_symbol(currency: list) -> list:
    return [{'symbol': c.get('symbol'), 'price': to_float(c.get('lastPrice'))} for c in currency]


def load_symbols_currencies(currency: list, state_data: dict) -> dict:
    currencies = {}
    for cur in currency:
        symbol = cur.get('symbol', '').lower()
        if state_info := state_data.get(symbol):
            currencies.update({
                symbol: {
                    'pair': state_info['pair'],
                    'expiration': state_info.get('expiration'),
                    'price': to_float(cur.get('lastPrice'))
                }
            })
    return currencies


def load_funding_rates(funding_rates: list) -> list:
    return [
        {
            'symbol': funding_rate['symbol'].lower(),
            'funding_rate': to_float(funding_rate['fundingRate']),
            'time': to_date(funding_rate['timestamp']),
        } for funding_rate in funding_rates
    ]


def load_exchange_symbol_info(raw_data: list, assets_config: list) -> list:
    symbol_list = []
    for d in raw_data:
        wallet_asset = d.get('settlCurrency').upper()
        # TODO: support bitmex USDT, ETH and spot schema
        if wallet_asset != 'XBT':
            continue

        symbol = d.get('symbol')
        base_asset = d.get('underlying')
        quote_currency = d.get('quoteCurrency')
        quote_asset, expiration = _quote_asset(symbol, base_asset, quote_currency)
        system_base_asset = to_system_asset(base_asset)
        system_quote_asset = to_system_asset(quote_asset)
        base_asset_precision, quote_asset_precision = load_assets_precision(base_asset, quote_asset, assets_config)
        system_symbol = symbol.lower().replace('xbt', 'btc')
        tick = to_float(d.get('tickSize'))
        volume_tick = to_float(d.get('lotSize'))
        max_leverage = 100 if d.get('initMargin', 0) <= 0 else 1 / d['initMargin']

        # TODO: support other wallet calc
        face_price_data = {
            'is_quanto': d.get('isQuanto'),
            'is_inverse': d.get('isInverse'),
            'multiplier': d.get('multiplier'),
            'underlying_multiplier': d.get('underlyingToPositionMultiplier')
        }
        symbol_list.append(
            {
                'symbol': symbol,
                'system_symbol': system_symbol,
                'base_asset': base_asset,
                'quote_asset': quote_asset,
                'system_base_asset': system_base_asset,
                'system_quote_asset': system_quote_asset,
                'base_asset_precision': base_asset_precision,
                'quote_asset_precision': quote_asset_precision,
                'expiration': expiration,
                'expiration_date': to_date(d.get('expiry')),
                'pair': [base_asset.upper(), quote_asset.upper()],
                'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                'schema': OrderSchema.margin,
                'tick': tick,
                'volume_tick': volume_tick,
                'max_leverage': max_leverage,
                'wallet_asset': wallet_asset,
                'extra': {'face_price_data': face_price_data}
            }
        )
    return symbol_list


def _quote_asset(symbol, base_asset, quote_currency) -> tuple:
    quote_asset = symbol[len(base_asset):].upper()
    if re.search(r'\d{2}$', symbol):
        return quote_currency, quote_asset[-3:]
    return quote_asset, None


def load_assets_precision(base_asset: str, quote_asset: str, assets_config: list) -> Tuple[int, int]:
    base_asset_precision = 8
    quote_asset_precision = 8
    for asset_conf in assets_config:
        asset = asset_conf.get('asset', '').lower()
        scale = int(asset_conf.get('scale', 8))
        if asset == base_asset.lower():
            base_asset_precision = scale
        if asset == quote_asset.lower():
            quote_asset_precision = scale
    return base_asset_precision, quote_asset_precision


def store_order_side(order_side: int) -> Optional[str]:
    if order_side is None:
        return None
    if order_side == api.SELL:
        return var.BITMEX_SELL
    return var.BITMEX_BUY


def load_order_side(order_side: str) -> int:
    if order_side.lower() == var.BITMEX_SELL.lower():
        return api.SELL
    return api.BUY


def load_order_id(raw_data: dict) -> Optional[str]:
    return raw_data.get('clOrdID') or None


def load_order_data(schema: str, raw_data: dict, state_data: Optional[dict]) -> dict:
    iceberg_volume = to_float(raw_data.get('displayQty'))
    data = {
        'order_id': load_order_id(raw_data),
        'exchange_order_id': raw_data.get('orderID'),
        'symbol': raw_data.get('symbol'),
        'schema': schema,
        'volume': to_int(raw_data.get('orderQty')),
        'filled_volume': to_int(raw_data.get('cumQty')),
        'stop_price': to_float(raw_data.get('stopPx')),
        'side': load_order_side(raw_data.get('side')),
        'position_side': PositionSide.both,
        'price': to_float(raw_data.get('price')),
        'time': to_date(raw_data.get('timestamp')),
        'active': bool(raw_data.get('ordStatus') != "New"),
        'type': BitmexOrderTypeConverter.load_order_type(schema, raw_data.get('ordType')),
        'ttl': var.BITMEX_ORDER_TTL_MAP.get(raw_data.get('timeInForce')),
        'is_iceberg': bool(iceberg_volume),
        'iceberg_volume': iceberg_volume,
        'is_passive': bool(raw_data.get('execInst') == 'ParticipateDoNotInitiate'),
        'comments': raw_data.get('text')
    }
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
        })
    return data


def load_order_ws_data(schema: str, raw_data: dict, state_data: Optional[dict]) -> dict:
    data = {
        'oid': load_order_id(raw_data),
        'eoid': raw_data.get('orderID'),
        'sd': load_order_side(raw_data.get('side')),
        'ps': PositionSide.both,
        'tv': to_float(raw_data.get('lastQty')),
        'tp': to_float(raw_data.get('lastPx')),
        'vl': to_float(raw_data.get('orderQty')),
        'p': to_float(raw_data.get('price')),
        'st': load_ws_order_status(raw_data.get('ordStatus')),
        'lv': to_float(raw_data.get('leavesQty')),
        'fv': to_float(raw_data.get('cumQty')),
        'ap': to_float(raw_data.get('avgPx')),
        's': raw_data.get('symbol'),
        'stp': to_float(raw_data.get('stopPx')),
        'tm': to_iso_datetime(raw_data.get('timestamp')),
        't': BitmexOrderTypeConverter.load_order_type(schema, raw_data.get('ordType')),
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_ws_order_status(bitmex_order_status: Optional[str]) -> Optional[str]:
    return var.BITMEX_ORDER_STATUS_MAP.get(bitmex_order_status) or api.OrderState.closed


def load_position_side_by_volume(volume: Optional[float]) -> Optional[int]:
    if isinstance(volume, (int, float)):
        if volume > 0:
            return api.BUY
        elif volume < 0:
            return api.SELL
    return None


def load_ws_position_action(state_volume: float, volume: float) -> str:
    if not state_volume and volume:
        return 'create'
    elif state_volume and not volume:
        return 'delete'
    elif state_volume and volume and (
            (state_volume > 0 > volume) or
            (state_volume < 0 < volume)
    ):
        return 'reverse'
    return 'update'


def load_position_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    state_volume = to_float(raw_data.get('state_volume'))
    volume = to_float(raw_data.get('currentQty'))
    side = load_position_side_by_volume(volume)
    unrealised_pnl = to_xbt(raw_data.get('unrealisedPnl'))
    leverage_type, leverage = load_leverage(raw_data)
    _timestamp = raw_data.get('timestamp') or datetime.now()
    data = {
        'tm': to_iso_datetime(_timestamp),
        's': raw_data.get('symbol'),
        'ps': PositionSide.both,
        'mp': to_float(raw_data.get('markPrice')),
        'upnl': unrealised_pnl,
        'vl': volume,
        'lp': to_float(raw_data.get('liquidationPrice')),
        'ep': to_float(raw_data.get('avgEntryPrice')),
        'sd': side if side is not None else raw_data.get('side'),
        'lvrp': leverage_type,
        'lvr': leverage,
        'act': load_ws_position_action(state_volume, volume),
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('id')).lower()
    }
    return data


def load_api_key_permissions(raw_data: dict, api_key: str, schemas: iter) -> dict:
    for acc in raw_data:
        if acc.get('id') == api_key:
            if 'order' in acc.get('permissions'):
                return {schema: (True if schema == OrderSchema.margin else False) for schema in schemas}
            else:
                return {schema: False for schema in schemas}
    return {schema: False for schema in schemas}


def load_trade_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    return load_quote_data(raw_data, state_data)


def load_quote_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_time = to_date(raw_data.get('timestamp'))
    data = {
        'time': quote_time,
        'symbol': raw_data.get('symbol'),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side')),
    }
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_ws_quote_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_time = to_iso_datetime(raw_data.get('timestamp'))
    data = {
        'tm': quote_time,
        's': raw_data.get('symbol'),
        'p': to_float(raw_data.get('price')),
        'vl': raw_data.get('size'),
        'sd': load_order_side(raw_data.get('side')),
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_quote_bin_data(raw_data: dict, state_data: Optional[dict], binsize=None) -> dict:
    quote_bin_time = to_date(raw_data.get('timestamp')) - binsize2timedelta(binsize)
    data = {
        'time': quote_bin_time,
        'symbol': raw_data.get('symbol'),
        'open_price': to_float(raw_data.get('open')),
        'close_price': to_float(raw_data.get('close')),
        'high_price': to_float(raw_data.get('high')),
        'low_price': to_float(raw_data.get('low')),
        'volume': raw_data.get('volume')
    }
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_ws_quote_bin_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    quote_bin_time = to_iso_datetime(raw_data.get('timestamp'))
    data = {
        'tm': quote_bin_time,
        's': raw_data.get('symbol'),
        'opp': to_float(raw_data.get('open')),
        'clp': to_float(raw_data.get('close')),
        'hip': to_float(raw_data.get('high')),
        'lop': to_float(raw_data.get('low')),
        'vl': raw_data.get('volume')
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def binsize2timedelta(binsize):
    return timedelta(seconds=BinSize(binsize).to_sec)


def load_order_book_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    symbol = raw_data.get('symbol')
    price = to_float(raw_data.get('price'))
    _id = generate_order_book_id(price, state_data)
    data = {
        'id': _id,
        'symbol': symbol,
        'price': price,
        'volume': raw_data.get('size'),
        'side': load_order_side(raw_data.get('side'))
    }
    if isinstance(state_data, dict):
        data.update({
            'schema': state_data.get('schema'),
            'system_symbol': state_data.get('system_symbol')
        })
    return data


def load_ws_order_book_data(raw_data: dict, state_data: Optional[dict], price_by_id: dict) -> dict:
    _id = raw_data.get('id')
    symbol = raw_data.get('symbol')
    price = to_float(raw_data.get('price') or to_float(price_by_id[symbol].get(_id)))
    _id = generate_order_book_id(price, state_data)
    data = {
        'id': _id,
        's': raw_data.get('symbol'),
        'p': price,
        'vl': raw_data.get('size'),
        'sd': load_order_side(raw_data.get('side'))
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def quote2bin(quote: dict) -> dict:
    return {
        's': quote['s'],
        'tm': quote['tm'],
        'opp': quote['p'],
        'clp': quote['p'],
        'hip': quote['p'],
        'lop': quote['p'],
        'vl': quote['vl'],
        'ss': quote.get('ss')
    }


def update_quote_bin(quote_bin: dict, quote: dict) -> dict:
    quote_bin['tm'] = quote['tm']
    quote_bin['clp'] = quote['p']
    quote_bin['hip'] = max(quote_bin['hip'], quote['p'])
    quote_bin['lop'] = min(quote_bin['lop'], quote['p'])
    quote_bin['vl'] += quote['vl']
    quote_bin['ss'] = quote.get('ss')
    return quote_bin


def load_wallet_data(raw_data: dict, is_for_ws=False) -> dict:
    if is_for_ws:
        return load_ws_wallet_detail_data(raw_data)
    return {
        'balances': [load_wallet_detail_data(raw_data)],
        'extra_data': None
    }


def load_wallet_detail_data(raw_data: dict, asset: str = None) -> dict:
    if asset and asset.lower() != raw_data.get('currency', '').lower():
        raise ConnectorError(f"Invalid asset {asset}.")
    return {
        'currency': raw_data.get('currency', '').upper(),
        'balance': to_xbt(raw_data.get('walletBalance')),
        'withdraw_balance': to_xbt(raw_data.get('withdrawableMargin')),
        'unrealised_pnl': to_xbt(raw_data.get('unrealisedPnl')),
        'margin_balance': to_xbt(raw_data.get('marginBalance')),
        'maint_margin': to_xbt(raw_data.get('maintMargin')),
        'init_margin': to_xbt(raw_data.get('initMargin')),
        'available_margin': to_xbt(raw_data.get('availableMargin')),
        'type': to_wallet_state_type(to_xbt(raw_data.get('maintMargin')))
    }


def load_ws_wallet_detail_data(raw_data: dict, asset: str = None) -> dict:
    if asset and asset.lower() != raw_data.get('currency', '').lower():
        raise ConnectorError(f"Invalid asset {asset}.")
    return {
        'cur': raw_data.get('currency', '').upper(),
        'bl': to_xbt(raw_data.get('walletBalance')),
        'wbl': to_xbt(raw_data.get('withdrawableMargin')),
        'upnl': to_xbt(raw_data.get('unrealisedPnl')),
        'mbl': to_xbt(raw_data.get('marginBalance')),
        'mm': to_xbt(raw_data.get('maintMargin')),
        'im': to_xbt(raw_data.get('initMargin')),
        'am': to_xbt(raw_data.get('availableMargin')),
        't': to_wallet_state_type(to_xbt(raw_data.get('maintMargin')))
    }


def load_wallet_asset_balance(raw_data: dict) -> dict:
    data = {
        raw_data.get('currency', '').lower(): to_xbt(raw_data.get('walletBalance')),
    }
    return data


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def load_commissions(commissions: dict) -> list:
    commissions_list = []
    for symbol, commission in commissions.items():
        for vip in var.BITMEX_VIP_LEVELS:
            commissions_list.append(
                {
                    'symbol': symbol.lower(),
                    'maker': to_float(commission['makerFee']),
                    'taker': to_float(vip['taker']),
                    'type': vip['type'],
                }
            )
    return commissions_list


def load_vip_level(trading_volume: Union[str, float]) -> str:
    trading_volume = to_float(trading_volume)
    if trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP4']:
        vip_level = '4'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP3']:
        vip_level = '3'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP2']:
        vip_level = '2'
    elif trading_volume >= var.BITMEX_AVERAGE_DAILY_VOLUME['VIP1']:
        vip_level = '1'
    else:
        vip_level = '0'
    return vip_level


def to_xbt(value: int):
    if isinstance(value, int):
        return round(value / 10 ** 8, 8)
    return to_float(value)


def to_date(token: Union[datetime, str]) -> Optional[datetime]:
    if not token:
        return None
    if isinstance(token, datetime):
        return token
    try:
        return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT)
    except (ValueError, TypeError, IndexError):
        return None


def to_iso_datetime(token: Union[datetime, str]) -> Optional[str]:
    if not token:
        return None
    try:
        if isinstance(token, datetime):
            return token.strftime(api.DATETIME_FORMAT)
        elif isinstance(token, str):
            return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT).strftime(api.DATETIME_FORMAT)
    except (ValueError, TypeError, IndexError):
        return None


def to_float(token: Union[int, float, str, None]) -> Optional[float]:
    try:
        return float(token)
    except (ValueError, TypeError):
        return 0.0


def to_int(token: Union[int, float, str, None]) -> Optional[int]:
    try:
        return int(token)
    except (ValueError, TypeError):
        return 0


def symbol2stock(symbol):
    return symbol.upper() if symbol is not None else None


def stock2symbol(symbol):
    return symbol.lower() if symbol is not None else None


def split_order_book(ob_items, state_data: Optional[dict]):
    result = {api.BUY: [], api.SELL: []}
    for _ob in ob_items:
        data = load_order_book_data(_ob, state_data)
        if _ob['side'] == var.BITMEX_BUY:
            result[api.BUY].append(data)
        elif _ob['side'] == var.BITMEX_SELL:
            result[api.SELL].append(data)
    return result


def filter_order_book(
    splitted_ob: Dict[int, list],
    min_volume_buy: float = None,
    min_volume_sell: float = None,
) -> Dict[int, list]:
    filtered_ob = splitted_ob
    if min_volume_buy is not None and min_volume_sell is not None:
        filtered_ob[api.BUY] = [
            buy_ob for buy_ob in filtered_ob[api.BUY]
            if buy_ob.get('volume') >= min_volume_buy
        ]
        filtered_ob[api.SELL] = [
            sell_ob for sell_ob in filtered_ob[api.SELL]
            if sell_ob.get('volume') >= min_volume_sell
        ]
    elif min_volume_buy is not None:
        filtered_ob[api.BUY] = [
            buy_ob for buy_ob in filtered_ob[api.BUY]
            if buy_ob.get('volume') >= min_volume_buy
        ]
    elif min_volume_sell is not None:
        filtered_ob[api.SELL] = [
            sell_ob for sell_ob in filtered_ob[api.SELL]
            if sell_ob.get('volume') >= min_volume_sell
        ]
    return filtered_ob


def slice_order_book(splitted_ob: Dict[int, list], depth: int, offset: int) -> Dict[int, list]:
    if offset and depth:
        return {
            api.BUY: splitted_ob[api.BUY][offset:depth + offset],
            api.SELL: splitted_ob[api.SELL][-offset-depth:-offset]
        }
    elif depth:
        return {
            api.BUY: splitted_ob[api.BUY][:depth],
            api.SELL: splitted_ob[api.SELL][-depth:]
        }
    elif offset:
        return {
            api.BUY: splitted_ob[api.BUY][offset:],
            api.SELL: splitted_ob[api.SELL][:-offset]
        }
    return splitted_ob


def load_leverage(raw_data: dict) -> tuple:
    if raw_data.get('crossMargin'):
        return LeverageType.cross, to_float(raw_data.get('leverage'))
    else:
        return LeverageType.isolated, to_float(raw_data.get('leverage'))


def store_leverage(leverage_type: str, leverage: float) -> float:
    if leverage_type == LeverageType.cross:
        return var.BITMEX_CROSS_LEVERAGE_TYPE_PARAM
    return leverage or 0


def load_position(raw_data: dict, schema: str) -> dict:
    now = datetime.now()
    return {
        'time': now,
        'schema': schema,
        'symbol': raw_data.get('symbol'),
        'side': load_position_side_by_volume(to_float(raw_data.get('currentQty'))),
        'position_side': PositionSide.both,
        'volume': to_float(raw_data.get('currentQty')),
        'entry_price': to_float(raw_data.get('avgEntryPrice')),
        'mark_price': to_float(raw_data.get('markPrice')),
        'unrealised_pnl': to_xbt(raw_data.get('unrealisedPnl')),
        'leverage_type': load_leverage(raw_data)[0],
        'leverage': to_float(raw_data.get('leverage')),
        'liquidation_price': to_float(raw_data.get('liquidationPrice')),
        }


def load_positions_list(raw_data: list, schema: str) -> list:
    return [load_position(data, schema) for data in raw_data if to_float(data.get('currentQty')) != 0]
