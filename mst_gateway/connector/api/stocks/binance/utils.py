from datetime import datetime, timezone
from typing import Union, Optional
from mst_gateway.connector import api
from mst_gateway.calculator import BinanceFinFactory
from mst_gateway.connector.api.utils.utils import (
    convert_to_currency, load_wallet_summary_in_usd, load_wallet_summary_margin3_in_usd
)
from mst_gateway.connector.api.stocks.binance.var import BinancePositionSideMode
from mst_gateway.connector.api.types.order import LeverageType, OrderSchema
from mst_gateway.utils import delta
from ...utils import time2timestamp
from .....exceptions import ConnectorError
from . import var
from .converter import BinanceOrderTypeConverter
from ...types.asset import to_system_asset
from ...utils.order_book import generate_order_book_id


def load_symbol_data(schema: str, raw_data: Optional[dict], state_data: Optional[dict]) -> dict:
    schema = schema.lower()
    raw_data = raw_data if raw_data else {}
    state_data = state_data if state_data else {}
    symbol = state_data.get('symbol') or raw_data.get('symbol')
    symbol_time = to_date(raw_data.get('closeTime'))
    price = to_float(raw_data.get('lastPrice'))
    price_change = to_float(raw_data.get('priceChange'))
    price24 = to_float(price - price_change)
    face_price, _reversed = BinanceFinFactory.calc_face_price(symbol, price, schema=schema)
    data = {
        'time': symbol_time,
        'symbol': symbol,
        'schema': schema,
        'price': price,
        'price24': price24,
        'delta': delta(price, price24),
        'face_price': face_price,
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'reversed': _reversed,
        'volume24': to_float(raw_data.get('volume')),
        'mark_price': price,
        'high_price': to_float(raw_data.get('highPrice')),
        'low_price': to_float(raw_data.get('lowPrice'))
    }
    if isinstance(state_data, dict):
        data.update({
            'expiration': state_data.get('expiration'),
            'expiration_date': state_data.get('expiration_date'),
            'pair': state_data.get('pair'),
            'tick': state_data.get('tick'),
            'volume_tick': state_data.get('volume_tick'),
            'system_symbol': state_data.get('system_symbol'),
            'symbol_schema': state_data.get('symbol_schema'),
            'created': to_date(state_data.get('created')),
            'max_leverage': state_data.get('max_leverage')
        })
    return data


def load_futures_symbol_data(schema: str, raw_data: Optional[dict], state_data: Optional[dict]) -> dict:
    raw_data = raw_data if raw_data else {}
    if data := load_symbol_data(schema, raw_data, state_data):
        data['mark_price'] = to_float(raw_data.get('markPrice'))
    return data


def load_exchange_symbol_info(raw_data: list, schema: str, valid_symbols: list = None) -> list:
    symbol_list = []
    for d in raw_data:
        if valid_symbols and d.get('symbol') not in valid_symbols:
            continue
        if d.get('status') == 'TRADING':
            system_base_asset = to_system_asset(d.get('baseAsset'))
            system_quote_asset = to_system_asset(d.get('quoteAsset'))
            system_symbol = f"{system_base_asset}{system_quote_asset}"

            tick = get_tick_from_symbol_filters(d, 'PRICE_FILTER', 'tickSize')
            volume_tick = get_tick_from_symbol_filters(d, 'LOT_SIZE', 'stepSize')

            symbol_list.append({
                'symbol': d.get('symbol'),
                'system_symbol': system_symbol.lower(),
                'schema': schema,
                'symbol_schema': schema,
                'base_asset': d.get('baseAsset'),
                'quote_asset': d.get('quoteAsset'),
                'system_base_asset': system_base_asset,
                'system_quote_asset': system_quote_asset,
                'expiration': None,
                'expiration_date': None,
                'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                'tick': tick,
                'volume_tick': volume_tick,
                'max_leverage': None
            })
    return symbol_list


def load_futures_symbol_expiration_date(expiration: Optional[str]) -> Optional[datetime]:
    try:
        return datetime(
            year=int(f"{str(datetime.now().year)[:2]}{expiration[:2]}"),
            month=int(expiration[2:4]),
            day=int(expiration[4:]),
            hour=8,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )
    except (ValueError, TypeError, IndexError):
        return None


def _load_futures_exchange_symbol_info(raw_data: list, leverage_data: dict, schema: str, status_field: str) -> list:
    symbol_list = []
    for d in raw_data:
        if d.get(status_field) == 'TRADING':
            system_base_asset = to_system_asset(d.get('baseAsset'))
            system_quote_asset = to_system_asset(d.get('quoteAsset'))
            expiration = None
            system_symbol = f"{system_base_asset}{system_quote_asset}"
            if not validate_symbol_pair_and_assets(d):
                continue
            if d.get('contractType', '').upper() != 'PERPETUAL':
                try:
                    expiration = d['symbol'].split('_')[1]
                    system_symbol = f"{system_symbol}_{expiration}"
                except (KeyError, IndexError):
                    expiration = None

            tick = get_tick_from_symbol_filters(d, 'PRICE_FILTER', 'tickSize')
            volume_tick = get_tick_from_symbol_filters(d, 'LOT_SIZE', 'stepSize')
            _symbol = d.get('symbol') if expiration is None else d.get('symbol', '')[:len(f"_{expiration}")]
            max_leverage = 100.0
            leverage_brackets = leverage_data.get(_symbol.lower(), [])
            if leverage_brackets and leverage_brackets[0].get('initialLeverage'):
                max_leverage = to_float(leverage_brackets[0]['initialLeverage'])

            symbol_list.append(
                {
                    'symbol': d.get('symbol'),
                    'system_symbol': system_symbol.lower(),
                    'base_asset': d.get('baseAsset'),
                    'quote_asset': d.get('quoteAsset'),
                    'system_base_asset': system_base_asset,
                    'system_quote_asset': system_quote_asset,
                    'expiration': expiration,
                    'expiration_date': load_futures_symbol_expiration_date(expiration),
                    'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                    'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                    'schema': schema.lower(),
                    'symbol_schema': schema.lower(),
                    'tick': tick,
                    'volume_tick': volume_tick,
                    'max_leverage': max_leverage,
                    'leverage_brackets': leverage_brackets,
                }
            )
    return symbol_list


def load_futures_exchange_symbol_info(raw_data: list, leverage_data: dict) -> list:
    return _load_futures_exchange_symbol_info(raw_data, leverage_data, OrderSchema.futures, 'status')


def load_futures_coin_exchange_symbol_info(raw_data: list, leverage_data: dict) -> list:
    return _load_futures_exchange_symbol_info(raw_data, leverage_data, OrderSchema.futures_coin, 'contractStatus')


def validate_symbol_pair_and_assets(raw_data):
    pair = raw_data.get('pair', '').lower()
    base_asset = raw_data.get('baseAsset', '').lower()
    quote_asset = raw_data.get('quoteAsset', '').lower()
    if pair != f'{base_asset}{quote_asset}':
        return False
    return True


def get_tick_from_symbol_filters(symbol_data, filter_name, parameter_name):
    """
    Extracts tick value (price tick or lot tick) from symbol data
    based on filter name and parameter name.

    """
    result = None
    for data in symbol_data.get('filters', []):
        if data.get('filterType') == filter_name:
            result = data.get(parameter_name)
            break
    return to_float(result)


def load_trade_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    data = {
        'time': to_date(raw_data.get('time')),
        'price': to_float(raw_data.get('price')),
        'volume': raw_data.get('qty'),
        'side': load_order_side(raw_data.get('isBuyerMaker'))
    }
    if isinstance(state_data, dict):
        data.update({
            'symbol': state_data.get('symbol'),
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_order_side(order_side: bool) -> int:
    if order_side:
        return api.BUY
    return api.SELL


def store_order_side(side: int) -> str:
    if side:
        return var.BINANCE_ORDER_SIDE_SELL
    return var.BINANCE_ORDER_SIDE_BUY


def store_order_type(order_type: str) -> str:
    converter = BinanceOrderTypeConverter
    return converter.store_type(order_type)


def load_order_book_side(order_side: str) -> int:
    if order_side == 'bids':
        return api.BUY
    return api.SELL


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
                         offset, depth, state_data: Optional[dict]) -> Union[list, dict]:
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

    resp = {} if split else []
    for k, v in _raw_data.items():
        _side = load_order_book_side(k)
        if side is not None and not side == _side:
            continue
        for item in v:
            price = to_float(item[0])
            _i = {
                'id': generate_order_book_id(price, state_data),
                'symbol': symbol,
                'price': price,
                'volume': to_float(item[1]),
                'side': _side
            }
            if isinstance(state_data, dict):
                _i.update({
                    'schema': state_data.get('schema'),
                    'system_symbol': state_data.get('system_symbol'),
                })
            if split:
                resp.setdefault(_side, []).append(_i)
            else:
                resp.append(_i)
    return resp


def load_quote_bin_data(raw_data: list, state_data: Optional[dict]) -> dict:
    data = {
        'time': to_date(raw_data[0]),
        'open_price': to_float(raw_data[1]),
        'close_price': to_float(raw_data[4]),
        'high_price': to_float(raw_data[2]),
        'low_price': to_float(raw_data[3]),
        'volume': raw_data[5]
    }
    if isinstance(state_data, dict):
        data.update({
            'symbol': state_data.get('symbol'),
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_order_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    _time_field = raw_data.get('time') or raw_data.get('transactTime') or raw_data.get('updateTime')
    _time = to_date(_time_field) or datetime.now()
    data = {
        'time': _time,
        'exchange_order_id': str(raw_data.get('orderId')),
        'symbol': raw_data.get('symbol'),
        'volume': to_float(raw_data.get('origQty')),
        'filled_volume': to_float(raw_data.get('cumQty')),
        'stop': to_float(raw_data.get('stopPrice')),
        'side': raw_data.get('side'),
        'price': to_float(raw_data.get('price')),
        'active': raw_data.get('status') != "NEW",
        'type': raw_data.get('type'),
        'execution': raw_data.get('type'),
    }
    if isinstance(state_data, dict):
        order_type_and_exec = load_order_type_and_exec(state_data.get('schema'), raw_data.get('type').upper())
        data.update({
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema'),
            **order_type_and_exec
        })
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('address')).lower()
    }
    return data


def load_api_key_permissions(raw_data: dict, schemas: iter) -> dict:
    schema_handlers = {
        OrderSchema.exchange: True,
        OrderSchema.margin2: raw_data.get('enableMargin', False),
        OrderSchema.margin3: raw_data.get('enableMargin', False),
        OrderSchema.futures: raw_data.get('enableFutures', False),
        OrderSchema.futures_coin: raw_data.get('enableFutures', False),
    }
    return {schema: schema_handlers.get(schema, False) for schema in schemas}


def load_spot_wallet_data(raw_data: dict, currencies: dict,
                          assets: Union[list, tuple], fields: Union[list, tuple], schema: str) -> dict:
    balances, extra_balances = _spot_balance_data(raw_data.get('balances'))
    total_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'balances': balances,
        'extra_data': None,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def load_ws_spot_wallet_data(raw_data: dict, currencies: dict,
                             assets: Union[list, tuple], fields: Union[list, tuple], schema: str) -> dict:
    balances, extra_balances = _spot_ws_balance_data(raw_data.get('balances'))
    total_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields, is_for_ws=True)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'bls': balances,
        'ex': None,
        **_load_total_wallet_summary_list(total_balance, fields, is_for_ws=True)
    }


def load_spot_wallet_balances(raw_data: dict) -> list:
    return _spot_balance_data(raw_data.get('balances'))[0]


def load_spot_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    if not raw_data.get('balances'):
        return _mock_balance_data(asset)
    for a in raw_data.get('balances'):
        if a.get('asset', '').upper() == asset.upper():
            return _spot_balance_data([a])[0][0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_wallet_data(raw_data: dict, currencies: dict,
                            assets: Union[list, tuple], fields: Union[list, tuple],
                            extra_fields: Union[list, tuple], schema: str) -> dict:
    balances, extra_balances = _margin_balance_data(raw_data.get('userAssets'))
    total_balance = {}
    total_extra_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields)
    wallet_extra_summary_in_usd = load_wallet_summary_in_usd(currencies, extra_balances, extra_fields)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
        total_extra_balance[asset] = convert_to_currency(
            wallet_extra_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'balances': balances,
        'extra_data': {
            'trade_enabled': raw_data.get('tradeEnabled'),
            'transfer_enabled': raw_data.get('transferEnabled'),
            'borrow_enabled': raw_data.get('borrowEnabled'),
            'margin_level': to_float(raw_data.get('marginLevel')),
            'balances': extra_balances,
            **_load_total_wallet_summary_list(total_extra_balance, extra_fields)
        },
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def load_ws_margin_wallet_data(raw_data: dict, currencies: dict,
                               assets: Union[list, tuple], fields: Union[list, tuple],
                               extra_fields: Union[list, tuple], schema: str) -> dict:
    balances, extra_balances = _margin_ws_balance_data(raw_data.get('userAssets'))
    total_balance = {}
    total_extra_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields, is_for_ws=True)
    wallet_extra_summary_in_usd = load_wallet_summary_in_usd(currencies, extra_balances, extra_fields, is_for_ws=True)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
        total_extra_balance[asset] = convert_to_currency(
            wallet_extra_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'bls': balances,
        'ex': {
            'tre': raw_data.get('tradeEnabled'),
            'trse': raw_data.get('transferEnabled'),
            'bore': raw_data.get('borrowEnabled'),
            'mlvl': raw_data.get('marginLevel'),
            'bls': extra_balances,
            **_load_total_wallet_summary_list(total_extra_balance, extra_fields, is_for_ws=True)
        },
        **_load_total_wallet_summary_list(total_balance, fields, is_for_ws=True)
    }


def load_isolated_margin_wallet_data(raw_data: dict, currencies: dict,
                                     assets: Union[list, tuple], fields: Union[list, tuple],
                                     extra_fields: Union[list, tuple], schema: str) -> dict:
    balances = isolated_margin_balance_data(raw_data.get('assets'))
    total_balance = dict()
    wallet_summary_in_usd = load_wallet_summary_margin3_in_usd(currencies, balances, fields)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'balances': balances,
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def load_margin_wallet_balances(raw_data: dict) -> list:
    return _margin_balance_data(raw_data.get('userAssets'))


def load_isolated_margin_wallet_balances(raw_data: dict) -> list:
    return isolated_margin_balance_data(raw_data.get('assets'))


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


# TODO: remove
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


def get_interest_rates(asset_rates: list):
    _h1_rate = {}
    for rate in asset_rates:
        asset = rate.get('assetName', '').lower()
        _h1_rate.setdefault(asset, {})
        for spec in rate['specs']:
            _r = to_float(spec.get('dailyInterestRate')) or 0
            _h1_rate[asset].setdefault(str(spec.get('vipLevel')), round(_r * 100 / 24, 8))
    return _h1_rate


def _load_futures_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                              fields: Union[list, tuple], extra_fields: Union[list, tuple],
                              cross_collaterals: list, schema: str) -> dict:
    balances, extra_balances = _futures_balance_data(raw_data.get('assets'))
    _update_futures_extra_balances(extra_balances, cross_collaterals)
    total_balance = {}
    total_extra_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields)
    wallet_extra_summary_in_usd = load_wallet_summary_in_usd(currencies, extra_balances, extra_fields)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
        total_extra_balance[asset] = convert_to_currency(
            wallet_extra_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'balances': balances,
        'extra_data': {
            'trade_enabled': raw_data.get('canTrade'),
            'balances': extra_balances,
            **_load_total_wallet_summary_list(total_extra_balance, extra_fields)
        },
        **_load_total_wallet_summary_list(total_balance, fields)
    }


def _load_ws_futures_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                                 fields: Union[list, tuple], extra_fields: Union[list, tuple],
                                 cross_collaterals: list, schema: str) -> dict:
    balances, extra_balances = _ws_futures_balance_data(raw_data.get('assets'))
    _update_ws_futures_balances(balances, cross_collaterals)
    total_balance = {}
    total_extra_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields, is_for_ws=True)
    wallet_extra_summary_in_usd = load_wallet_summary_in_usd(currencies, extra_balances, extra_fields, is_for_ws=True)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
        total_extra_balance[asset] = convert_to_currency(
            wallet_extra_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    return {
        'bls': balances,
        'ex': {
            'tre': raw_data.get('canTrade'),
            **_load_total_wallet_summary_list(total_extra_balance, extra_fields, is_for_ws=True)
        },
        **_load_total_wallet_summary_list(total_balance, fields, is_for_ws=True)
    }


def load_futures_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                             fields: Union[list, tuple], extra_fields: Union[list, tuple],
                             cross_collaterals: list, schema: str) -> dict:
    return _load_futures_wallet_data(raw_data, currencies, assets, fields, extra_fields, cross_collaterals, schema)


def load_ws_futures_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                                fields: Union[list, tuple], extra_fields: Union[list, tuple],
                                cross_collaterals: list, schema: str) -> dict:
    return _load_ws_futures_wallet_data(raw_data, currencies, assets, fields, extra_fields, cross_collaterals, schema)


def load_futures_coin_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                                  fields: Union[list, tuple], extra_fields: Union[list, tuple],
                                  cross_collaterals: list, schema: str) -> dict:
    return load_futures_wallet_data(raw_data, currencies, assets, fields, extra_fields, cross_collaterals, schema)


def load_ws_futures_coin_wallet_data(raw_data: dict, currencies: dict, assets: Union[list, tuple],
                                     fields: Union[list, tuple], extra_fields: Union[list, tuple],
                                     cross_collaterals: list, schema: str) -> dict:
    return load_ws_futures_wallet_data(raw_data, currencies, assets, fields, extra_fields, cross_collaterals, schema)


def _update_futures_extra_balances(balances: list, cross_collaterals: list) -> list:
    for balance in balances:
        for collateral in cross_collaterals:
            if balance['currency'] == collateral['loanCoin']:
                balance['borrowed'] += to_float(collateral['loanAmount']) or 0.0
                balance['interest'] += to_float(collateral['interest']) or 0.0
    return balances


def _update_ws_futures_balances(balances: list, cross_collaterals: list) -> list:
    for balance in balances:
        for collateral in cross_collaterals:
            if balance['cur'] == collateral['loanCoin']:
                balance['bor'] += to_float(collateral['loanAmount']) or 0.0
                balance['ist'] += to_float(collateral['interest']) or 0.0
    return balances


def load_future_wallet_balances(raw_data: dict) -> list:
    return _futures_balance_data(raw_data.get('assets'))


def load_future_coin_wallet_balances(raw_data: dict) -> list:
    return _futures_balance_data(raw_data.get('assets'))


def load_futures_wallet_detail_data(raw_data: dict, asset: str,
                                    cross_collaterals: list, collateral_configs: list) -> dict:
    for a in raw_data.get('assets'):
        if a.get('asset', '').upper() == asset.upper():
            balance = _futures_balance_data([a])[0]
            _update_futures_extra_balances([balance], cross_collaterals)
            cross_collaterals = _load_cross_collaterals_data(
                cross_collaterals, collateral_configs, asset
            )
            balance['cross_collaterals'] = cross_collaterals
            return balance
    raise ConnectorError(f"Invalid asset {asset}.")


def _load_cross_collaterals_data(cross_collaterals_data: list, collateral_configs: list, asset: str) -> list:
    """ combining cross_collaterals data and collateral_configs data """

    collaterals = {}
    for collateral_coin in cross_collaterals_data:
        if collateral_coin.get('loanCoin', '').upper() == asset.upper():
            data = {
                'collateral_currency': collateral_coin.get('collateralCoin'),
                'locked': to_float(collateral_coin.get('locked')),
                'borrowed': to_float(collateral_coin.get('loanAmount')),
                'current_collateral_rate': to_float(collateral_coin.get('currentCollateralRate')),
                'principal_for_interest': to_float(collateral_coin.get('principalForInterest')),
                'interest': to_float(collateral_coin.get('interest')),
                'interest_free_limit_used': to_float(collateral_coin.get('interestFreeLimitUsed')),
            }
            collaterals[collateral_coin.get('collateralCoin')] = data
    cross_collaterals = [{
        'rate': to_float(config.get('rate')),
        'margin_call_collateral_rate': to_float(config.get('marginCallCollateralRate')),
        'liquidation_collateral_rate': to_float(config.get('liquidationCollateralRate')),
        'current_collateral_rate': to_float(config.get('currentCollateralRate')),
        'interest_rate': to_float(config.get('interestRate')),
        'interest_grace_period': to_float(config.get('interestGracePeriod')),
        **collaterals.get(config.get('collateralCoin'), {})
    } for config in collateral_configs]
    return cross_collaterals


def load_futures_cross_collaterals_data(cross_collaterals: list) -> list:
    data = [{
        'collateral_currency': cross.get('collateralCoin'),
        'borrowed_currency': cross.get('loanCoin'),
        'locked': to_float(cross.get('locked')),
        'borrowed': to_float(cross.get('loanAmount')),
    } for cross in cross_collaterals]
    return data


def load_exchange_asset_balance(raw_data: list) -> dict:
    balances = {}
    for balance in raw_data:
        balances[balance.get('asset', '').lower()] = to_float(balance.get('free', 0))
    return balances


def load_margin_asset_balance(raw_data: list) -> dict:
    return load_exchange_asset_balance(raw_data)


def load_futures_asset_balance(raw_data: list) -> dict:
    balances = {}
    for balance in raw_data:
        balances[balance.get('asset', '').lower()] = to_float(balance.get('balance', 0))
    return balances


def load_futures_coin_asset_balance(raw_data: list) -> dict:
    return load_futures_asset_balance(raw_data)


def _ws_wallet(balances: list, state_balances: dict, state_data: dict, currencies: dict,
               assets: Union[list, tuple], fields: Union[list, tuple], schema: str):
    balances.extend([v for v in state_balances.values()])
    total_balance = {}
    wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields, is_for_ws=True)
    for asset in assets:
        total_balance[asset] = convert_to_currency(
            wallet_summary_in_usd, currencies.get(to_exchange_asset(asset, schema))
        )
    state_data.update({
        **_load_total_wallet_summary_list(total_balance, fields, is_for_ws=True),
        'bls': balances
    })
    return state_data


def ws_spot_wallet(raw_data: dict, state_data: dict, currencies: dict,
                   assets: Union[list, tuple], fields: Union[list, tuple], schema: str):
    state_data.pop('*', None)
    _state_balances = state_data.pop('bls', {})
    _balances, _extra_balances = _spot_ws_balance_data(raw_data.get('B'), _state_balances)
    return _ws_wallet(_balances, _state_balances, state_data, currencies, assets, fields, schema)


def ws_margin_wallet(raw_data: dict, state_data: dict, currencies: dict,
                     assets: Union[list, tuple], fields: Union[list, tuple], schema):
    state_data.pop('*', None)
    _state_balances = state_data.pop('bls', {})
    _balances = ws_margin_balance_data(raw_data.get('B'), _state_balances)
    return _ws_wallet(_balances, _state_balances, state_data, currencies, assets, fields, schema)


def ws_margin_balance_data(balances: list, state_balances: dict):
    result = []
    for b in balances:
        _currency = b['a'].lower()
        _currency_state = state_balances.pop(_currency, {})
        _free = to_float(b['f'])
        _locked = to_float(b['l'])
        _balance = round(_free + _locked, 8)
        result.append({
            'cur': b['a'],
            'bl': _balance,
            'wbl': _currency_state.get('wbl', 0),
            'bor': _currency_state.get('bor', 0),
            'abor': _currency_state.get('abor', 0),
            'ist': _currency_state.get('ist', 0),
            'istr': _currency_state.get('istr', 0),
            'mbl': _balance,
            'im': _locked,
            'am': _free,
            't': 'hold',
        })
    return result


def ws_futures_wallet(raw_data: dict, state_data: dict, currencies: dict,
                      assets: Union[list, tuple], fields: Union[list, tuple], schema):
    state_data.pop('*', None)
    _state_balances = state_data.pop('bls', {})
    _balances = ws_futures_balance_data(
        raw_data.get('a', {}).get('B', []), raw_data.get('a', {}).get('P', []), _state_balances)
    return _ws_wallet(_balances, _state_balances, state_data, currencies, assets, fields, schema)


def ws_futures_balance_data(balances: list, position: list, state_balances: dict):
    position_upnl = {}
    for p in position:
        position_upnl.setdefault(p['ma'].lower(), 0)
        position_upnl[p['ma'].lower()] += to_float(p['up'])
    result = []
    for b in balances:
        _currency = b['a'].lower()
        _currency_state = state_balances.pop(_currency, {})
        _unrealised_pnl = position_upnl.get(_currency)
        margin_balance = to_float(b['wb']) + (_unrealised_pnl or 0)
        maint_margin = _currency_state.get('mm', 0)
        result.append({
            'cur': b['a'],
            'bl': to_float(b['wb']),
            'wbl': _currency_state.get('wbl', 0),
            'bor': _currency_state.get('bor', 0),
            'ist': _currency_state.get('ist', 0),
            'upnl': _unrealised_pnl,
            'mbl': margin_balance,
            'mm': maint_margin,
            'im': _currency_state.get('im', 0),
            'am': margin_balance - maint_margin,
            't': to_wallet_state_type(_unrealised_pnl),
        })
    return result


def _mock_balance_data(asset) -> dict:
    return {
        'currency': asset.upper(),
        'balance': 0.0,
        'withdraw_balance': 0.0,
        'borrowed': 0.0,
        'available_borrow': 0.0,
        'interest': 0.0,
        'interest_rate': 0.0,
        'unrealised_pnl': 0.0,
        'margin_balance': 0.0,
        'maint_margin': 0.0,
        'init_margin': 0.0,
        'available_margin': 0.0,
        'type': to_wallet_state_type(0),
    }


def _spot_balance_data(balances: list):
    result = []
    for b in balances:
        asset = b['asset']
        free = to_float(b['free'])
        locked = to_float(b['locked'])
        balance = round(free + locked, 8)
        result.append(
            {
                'currency': asset,
                'balance': balance,
                'withdraw_balance': free,
                'unrealised_pnl': 0,
                'margin_balance': balance,
                'maint_margin': 0,
                'init_margin': locked,
                'available_margin': free,
                'type': 'hold',
            }
        )
    return result, None


def _spot_ws_balance_data(balances: list, state_balances: dict = None):
    result = []
    for b in balances:
        asset = b['asset'] if 'asset' in b else b['a']
        if state_balances:
            state_balances.pop(asset.lower(), {})
        free = to_float(b['free'] if 'free' in b else b['f'])
        locked = to_float(b['locked'] if 'locked' in b else b['l'])
        balance = round(free + locked, 8)
        result.append(
            {
                'cur': asset,
                'bl': balance,
                'wbl': free,
                'upnl': 0,
                'mbl': balance,
                'mm': 0,
                'im': locked,
                'am': free,
                't': 'hold',
            }
        )
    return result, None


def _margin_balance_data(balances: list):
    result = []
    extra_result = []
    for b in balances:
        wd, ex_wd = _get_margin_balance(b)
        result.append(wd)
        extra_result.append(ex_wd)
    return result, extra_result


def _get_margin_balance(balance: dict):
    currency = balance['asset']
    _free = to_float(balance['free'])
    _locked = to_float(balance['locked'])
    borrowed = to_float(balance['borrowed'])
    interest = to_float(balance['interest'])
    _balance = round(_free + _locked, 8)
    withdraw_balance = to_float(balance['netAsset']) - (borrowed + interest)
    if withdraw_balance < 0:
        withdraw_balance = 0
    wallet_data = {
        'currency': currency,
        'balance': _balance,
        'withdraw_balance': withdraw_balance,
        'unrealised_pnl': 0,
        'margin_balance': _balance,
        'maint_margin': 0,
        'init_margin': _locked,
        'available_margin': _free,
        'type': 'hold',
    }
    extra_wallet_data = {
        'currency': currency,
        'borrowed': borrowed,
        'interest': interest,
    }
    return wallet_data, extra_wallet_data


def _margin_ws_balance_data(balances: list, max_borrow: float = None, interest_rate: float = None):
    result = []
    extra_result = []
    for b in balances:
        currency = b['asset']
        _free = to_float(b['free'])
        _locked = to_float(b['locked'])
        borrowed = to_float(b['borrowed'])
        interest = to_float(b['interest'])
        _balance = round(_free + _locked, 8)
        withdraw_balance = to_float(b['netAsset']) - (borrowed + interest)
        if withdraw_balance < 0:
            withdraw_balance = 0
        result.append({
            'cur': currency,
            'bl': _balance,
            'wbl': withdraw_balance,
            'upnl': 0,
            'mbl': _balance,
            'mm': 0,
            'im': _locked,
            'am': _free,
            't': 'hold',
        })
        extra_result.append({
            'cur': currency,
            'bor': borrowed,
            'abor': max_borrow,
            'ist': interest,
            'istr': interest_rate,
        })
    return result, extra_result


def isolated_margin_balance_data(balances: list, max_borrow: dict = None, interest_rate: dict = None):
    result = list()
    max_borrow_base_asset = _margin_max_borrow(max_borrow.get('base_asset')) if max_borrow else None
    max_borrow_quote_asset = _margin_max_borrow(max_borrow.get('quote_asset')) if max_borrow else None
    interest_rate_base_asset = interest_rate.get('base_asset') if max_borrow else None
    interest_rate_quote_asset = interest_rate.get('quote_asset') if max_borrow else None
    for b in balances:
        try:
            base_asset, _ = _get_margin_balance(b['baseAsset'], max_borrow_base_asset, interest_rate_base_asset)
            quote_asset, _ = _get_margin_balance(b['quoteAsset'], max_borrow_quote_asset, interest_rate_quote_asset)
            result.append({
                b['symbol'].lower(): {
                    'base_asset': base_asset,
                    'quote_asset': quote_asset,
                    'type': to_wallet_state_type('trade' in (base_asset.get('type'), quote_asset.get('type'))),
                    'margin_level': to_float(b.get('marginLevel')),
                    'margin_ratio': to_float(b.get('marginRatio')),
                    'trade_enabled': b.get('tradeEnabled'),
                }
            })
        except KeyError:
            continue
    return result


def _margin_max_borrow(data):
    if isinstance(data, dict):
        return to_float(data.get('amount'))
    return 0.0


def _futures_balance_data(balances: list):
    result = []
    extra_result = []
    for b in balances:
        currency = b['asset']
        result.append({
            'currency': currency,
            'balance': to_float(b['walletBalance']),
            'withdraw_balance': to_float(b['maxWithdrawAmount']),
            'unrealised_pnl': to_float(b['unrealizedProfit']),
            'margin_balance': to_float(b['marginBalance']),
            'maint_margin': to_float(b['maintMargin']),
            'init_margin': to_float(b['initialMargin']),
            'available_margin': to_float(b['maxWithdrawAmount']),
            'type': to_wallet_state_type(to_float(b['maintMargin'])),
        })
        extra_result.append({
            'currency': currency,
            'borrowed': 0.0,
            'interest': 0.0,
        })
    return result, extra_result


def _ws_futures_balance_data(balances: list):
    result = []
    extra_result = []
    for b in balances:
        currency = b['asset']
        result.append({
            'cur': currency,
            'bl': to_float(b['walletBalance']),
            'wbl': to_float(b['maxWithdrawAmount']),
            'upnl': to_float(b['unrealizedProfit']),
            'mbl': to_float(b['marginBalance']),
            'mm': to_float(b['maintMargin']),
            'im': to_float(b['initialMargin']),
            'am': to_float(b['maxWithdrawAmount']),
            't': to_wallet_state_type(to_float(b['maintMargin'])),
        })
        extra_result.append({
            'cur': currency,
            'bor': 0,
            'ist': 0,
        })
    return result, extra_result


def _load_total_wallet_summary_list(summary, fields, is_for_ws=False):
    total = dict()
    for field in fields:
        t_field = f'total_{field}'
        if is_for_ws:
            t_field = f't{field}'
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


def load_leverage_brackets_as_dict(data: list) -> dict:
    return {d['symbol'].lower(): d['brackets'] for d in data if d.get('brackets')}


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


def load_symbols_currencies(currency: list, state_data: dict) -> dict:
    currencies = {}
    for cur in currency:
        symbol = cur.get('symbol', '').lower()
        if state_info := state_data.get(symbol):
            currencies.update({
                symbol: {
                    'pair': state_info['pair'],
                    'expiration': state_info.get('expiration'),
                    'price': to_float(cur.get('price'))
                }
            })
    return currencies


def to_wallet_state_type(value):
    if bool(value):
        return 'trade'
    return 'hold'


def load_transaction_id(raw_data: dict) -> dict:
    data = {
        'transaction': raw_data.get('tranId')
    }
    return data


def load_borrow_data(raw_data: dict) -> dict:
    data = {
        'amount': to_float(raw_data.get('amount')),
        'collateral_asset': raw_data.get('collateralCoin'),
        'collateral_amount': to_float(raw_data.get('collateralAmount')),
        'transaction': raw_data.get('borrowId')
    }
    return data


def load_repay_data(raw_data: dict) -> dict:
    data = {
        'amount': raw_data.get('amount'),
        'collateral_asset': raw_data.get('collateralCoin'),
        'collateral_amount': raw_data.get('collateralAmount'),
        'transaction': raw_data.get('repayId')
    }
    return data


def load_commissions(raw_data: dict) -> list:
    return [
        {
            'maker': to_float(commission['makerCommission']),
            'taker': to_float(commission['takerCommission']),
            'type': f'VIP{commission["level"]}',
        } for commission in raw_data
    ]


def to_exchange_asset(asset: str, schema: str):
    if asset == 'usd' and schema != OrderSchema.futures_coin:
        return 'usdt'
    return asset


def load_trade_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
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
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        'p': to_float(raw_data.get('p')),
        'vl': to_float(raw_data.get('q')),
        'sd': load_order_side(raw_data.get('m')),
        's': raw_data.get('s')
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_quote_bin_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
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
    raw_data = raw_data.get('k', {})
    _timestamp = raw_data.get('t')
    data = {
        'tm': to_iso_datetime(_timestamp),
        'opp': to_float(raw_data.get("o")),
        'clp': to_float(raw_data.get("c")),
        'hip': to_float(raw_data.get("h")),
        'lop': to_float(raw_data.get('l')),
        'vl': to_float(raw_data.get('v'))
    }
    if isinstance(state_data, dict):
        data.update({
            's': state_data.get('symbol'),
            'ss': state_data.get('system_symbol')
        })
    return data


def load_order_book_ws_data(raw_data: dict, order: list, side: int, state_data: Optional[dict]) -> dict:
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

    data = {
        'id': generate_order_book_id(price, state_data),
        's': symbol,
        'p': price,
        'vl': to_float(order[1]),
        'sd': side
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_symbol_ws_data(schema: str, raw_data: dict, state_data: Optional[dict]) -> dict:
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
    schema = schema.lower()
    symbol = raw_data.get('s')
    price = to_float(raw_data.get('c'))
    price_change = to_float(raw_data.get('p'))
    price24 = to_float(price - price_change)
    face_price, _reversed = BinanceFinFactory.calc_face_price(symbol, price, schema=schema)
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        's': symbol,
        'p': price,
        'p24': price24,
        'dt': delta(price, price24),
        'fp': face_price,
        'bip': to_float(raw_data.get('b')),
        'asp': to_float(raw_data.get('a')),
        're': _reversed,
        'v24': to_float(raw_data.get('v')),
        'mp': to_float(raw_data.get('c')),
        'hip': to_float(raw_data.get("h")),
        'lop': to_float(raw_data.get('l'))
    }
    if isinstance(state_data, dict):
        data.update({
            'exp': state_data.get('expiration'),
            'expd': state_data.get('expiration_date'),
            'pa': state_data.get('pair'),
            'tck': state_data.get('tick'),
            'vt': state_data.get('volume_tick'),
            'ss': state_data.get('system_symbol'),
            'ssch': state_data.get('symbol_schema'),
            'crt': to_iso_datetime(to_date(state_data.get('created'))),
            'mlvr': state_data.get('max_leverage')
        })
    return data


def load_futures_symbol_ws_data(schema: str, raw_data: dict, state_data: Optional[dict]) -> dict:
    if data := load_symbol_ws_data(schema, raw_data, state_data):
        data['mp'] = to_float(raw_data.get('mp'))
    return data


def to_date(token: Union[datetime, int, str]) -> Optional[datetime]:
    if not token:
        return None
    if isinstance(token, datetime):
        return token
    try:
        if isinstance(token, str):
            return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT)
        elif isinstance(token, int):
            return datetime.fromtimestamp(token / 1000, tz=timezone.utc)
    except (ValueError, TypeError, IndexError):
        return None


def to_iso_datetime(token: Union[datetime, int, str]) -> Optional[str]:
    if not token:
        return None
    try:
        if isinstance(token, datetime):
            return token.strftime(api.DATETIME_FORMAT)
        elif isinstance(token, int):
            return datetime.fromtimestamp(token / 1000, tz=timezone.utc).strftime(api.DATETIME_FORMAT)
        elif isinstance(token, str):
            return datetime.strptime(token.split('Z')[0], api.DATETIME_FORMAT).strftime(api.DATETIME_FORMAT)
    except (ValueError, TypeError, IndexError):
        return None


def to_float(token: Union[int, float, str, None]) -> float:
    try:
        return float(token)
    except (ValueError, TypeError):
        return 0.0


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


def load_order_ws_data(raw_data: dict, state_data: Optional[dict]) -> dict:
    data = {
        'eoid': str(raw_data.get('i')),
        'sd': load_ws_order_side(raw_data.get('S')),
        'tv': to_float(raw_data.get('l')),
        'tp': to_float(raw_data.get('L')),
        'vl': to_float(raw_data.get('q')),
        'p': to_float(raw_data.get('p')),
        'st': load_ws_order_status(raw_data.get('X')),
        'lv': calculate_ws_order_leaves_volume(raw_data),
        'fv': to_float(raw_data.get('z')),
        'ap': calculate_ws_order_avg_price(raw_data),
        'tm': to_iso_datetime(raw_data.get('E')),
        's': raw_data.get('s'),
        'stp': to_float(raw_data['P']) if raw_data.get('P') else to_float(raw_data.get('sp')),
        'crt': to_iso_datetime(raw_data['O']) if raw_data.get('O') else to_date(raw_data.get('T')),
        't': raw_data.get('o', '').lower(),
        'exc': raw_data.get('o', '').lower(),
    }
    if isinstance(state_data, dict):
        order_type_and_exec = load_order_type_and_exec(state_data.get('schema'), raw_data.get('o', '').upper())
        data.update({
            'ss': state_data.get('system_symbol'),
            't': order_type_and_exec.get('type'),
            'exc':  order_type_and_exec.get('execution')
        })
    return data


def load_ws_order_status(binance_order_status: Optional[str]) -> Optional[str]:
    return var.BINANCE_ORDER_STATUS_MAP.get(binance_order_status) or api.OrderState.closed


def calculate_ws_order_leaves_volume(raw_data: dict) -> float:
    try:
        return to_float(raw_data['q']) - to_float(raw_data['z'])
    except (KeyError, TypeError):
        return 0.0


def calculate_ws_order_avg_price(raw_data: dict) -> float:
    if raw_data.get('ap'):  # Futures
        return to_float(raw_data['ap'])
    elif raw_data.get('Z') and to_float(raw_data.get('z')):  # Spot
        return to_float(raw_data['Z'])/to_float(raw_data['z'])
    else:
        return 0.0


def load_funding_rates(funding_rates: list) -> list:
    return [
        {
            'symbol': funding_rate['symbol'].lower(),
            'funding_rate': to_float(funding_rate['fundingRate']),
            'time': to_date(funding_rate['fundingTime']),
        } for funding_rate in funding_rates
    ]


def load_order_type_and_exec(schema: str, exchange_order_type: str) -> dict:
    converter = BinanceOrderTypeConverter
    return converter.load_type_and_exec(schema, exchange_order_type)


def get_mapping_for_schema(schema: str) -> Optional[dict]:
    """
    Retrieves order type parameter mapping data for the specified schema.

    """
    mapping_data = var.PARAMETERS_BY_ORDER_TYPE_MAP.get(schema)
    if not mapping_data:
        raise ConnectorError(f"Invalid schema parameter: {schema}")
    return mapping_data


def store_order_mapping_parameters(exchange_order_type: str, schema: str) -> list:
    data_for_schema = get_mapping_for_schema(schema)
    data = data_for_schema.get(exchange_order_type)
    if data:
        return data['params']
    return data_for_schema['LIMIT']['params']


def store_order_additional_parameters(exchange_order_type: str, schema: str) -> dict:
    data_for_schema = get_mapping_for_schema(schema)
    data = data_for_schema.get(exchange_order_type)
    if data:
        return data['additional_params']
    return data_for_schema['LIMIT']['additional_params']


def generate_parameters_by_order_type(main_params: dict, options: dict, schema: str) -> dict:
    """
    Fetches specific order parameters based on the order_type value and adds them
    to the main parameters.

    """
    order_type = main_params.pop('order_type', None)
    exchange_order_type = store_order_type(order_type)
    mapping_parameters = store_order_mapping_parameters(exchange_order_type, schema)
    options = assign_custom_parameter_values(options, schema)
    all_params = map_api_parameter_names(
        {'order_type': exchange_order_type, **main_params, **options}
    )
    new_params = dict()
    for param_name in mapping_parameters:
        value = all_params.get(param_name)
        if value:
            new_params[param_name] = value
    new_params.update(
        store_order_additional_parameters(exchange_order_type, schema)
    )
    return new_params


def assign_custom_parameter_values(options: Optional[dict], schema: Optional[str]) -> dict:
    """
    Changes the value of certain parameters according to Binance's specification.

    """
    new_options = dict()
    if 'ttl' in options:
        new_options['ttl'] = var.PARAMETER_NAMES_MAP.get(options.get('ttl'))
    if options.get('is_iceberg'):
        new_options['iceberg_volume'] = options['iceberg_volume'] or 0

    if options.get('is_passive') and schema in [api.OrderSchema.futures_coin, api.OrderSchema.futures]:
        new_options['ttl'] = var.PARAMETER_NAMES_MAP.get('GTX')
    return new_options


def map_api_parameter_names(params: dict) -> Optional[dict]:
    """
    Changes the name (key) of any parameters that have a different name in the Binance API.
    Example: 'ttl' becomes 'timeInForce'

    """
    tmp_params = dict()
    for param, value in params.items():
        if value is None:
            continue
        _param = var.PARAMETER_NAMES_MAP.get(param) or param
        tmp_params[_param] = value
    return tmp_params


def load_leverage(raw_data: list) -> tuple:
    for pos in raw_data:
        if pos.get('positionSide', '') == var.BinancePositionSideMode.BOTH:
            if pos.get('marginType', '') == LeverageType.cross:
                leverage_type = LeverageType.cross
            else:
                leverage_type = LeverageType.isolated
            leverage = to_float(pos.get('leverage')) or 20
            return leverage_type, leverage
    return LeverageType.cross, 20


def store_leverage(leverage_type: str) -> str:
    if leverage_type == LeverageType.cross:
        return var.BINANCE_LEVERAGE_TYPE_CROSS
    return var.BINANCE_LEVERAGE_TYPE_ISOLATED


def load_position_side_by_volume(position_amount: float) -> Optional[int]:
    if position_amount and position_amount < 0:
        return api.SELL
    if position_amount and position_amount > 0:
        return api.BUY
    return None


def load_ws_futures_position_leverage_type(margin_type: Optional[str]) -> Optional[str]:
    if margin_type and margin_type.lower() == LeverageType.cross:
        return LeverageType.cross
    if margin_type and margin_type.lower() == LeverageType.isolated:
        return LeverageType.isolated
    return None


def load_futures_position_ws_data(raw_data: dict, position_state_data: dict, state_data: Optional[dict],
                                  exchange_rates: dict, schema: str) -> dict:
    expiration = None
    unrealised_pnl = position_state_data['unrealised_pnl']
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        's': position_state_data['symbol'].lower(),
        'sd': position_state_data['side'],
        'vl': position_state_data['volume'],
        'ep': position_state_data['entry_price'],
        'mp': position_state_data['mark_price'],
        'upnl': unrealised_pnl,
        'lvrp': position_state_data['leverage_type'],
        'lvr': position_state_data['leverage'],
        'lp': position_state_data['liquidation_price'],
        'act': position_state_data['action']
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
        if exp := state_data.get('expiration', None):
            expiration = exp
    if schema == OrderSchema.futures_coin:
        try:
            asset = state_data.get('pair')[0].lower()
        except (TypeError, IndexError, AttributeError):
            asset = None
        unrealised_pnl = load_ws_futures_coin_position_unrealised_pnl(unrealised_pnl, exchange_rates, asset, expiration)
    else:
        unrealised_pnl = load_ws_futures_position_unrealised_pnl(unrealised_pnl, exchange_rates, expiration)
    data['upnl'] = unrealised_pnl
    return data


def load_ws_futures_position_unrealised_pnl(base: float, exchange_rates: dict, expiration: Optional[str]) -> dict:
    return {
        'base': base,
        'usd': base,
        'btc': to_btc(base, exchange_rates)
    }


def load_ws_futures_coin_position_unrealised_pnl(
        base: float, exchange_rates: dict, asset: str, expiration: Optional[str]) -> dict:
    if expiration and (asset_to_usd := exchange_rates.get(f"{asset}{expiration}".lower())):
        pass
    else:
        asset_to_usd = exchange_rates.get(asset.lower())

    try:
        usd = asset_to_usd * base
    except TypeError:
        usd = None
    return {
        'base': base,
        'usd': usd,
        'btc': to_btc(usd, exchange_rates)
    }


def to_btc(usd_value: float, exchange_rates: dict) -> Optional[float]:
    btc_to_usd = exchange_rates.get('btc')
    try:
        return usd_value / btc_to_usd
    except TypeError:
        return None


def load_position_leverage_type(position_data: dict) -> str:
    if position_data.get('isolated'):
        return LeverageType.isolated
    return LeverageType.cross


def load_positions_state(state_data: dict) -> dict:
    return {data['symbol'].lower(): data for data in state_data.values() if 'symbol' in data}


def load_futures_positions_state(account_info: dict) -> dict:
    positions_state = {}
    cross_wallet_balance = to_float(account_info.get('totalCrossWalletBalance'))
    for position in account_info.get('positions', []):
        if position['positionSide'].upper() == BinancePositionSideMode.BOTH:
            symbol = position['symbol'].lower()
            volume = to_float(position['positionAmt'])
            side = load_position_side_by_volume(volume)
            entry_price = to_float(position['entryPrice'])
            _unrealised_pnl = to_float(position['unrealizedProfit'])
            mark_price = BinanceFinFactory.calc_mark_price(volume, entry_price, _unrealised_pnl)
            positions_state[symbol] = {
                'symbol': symbol,
                'volume': volume,
                'side': side,
                'entry_price': entry_price,
                'mark_price': mark_price,
                'leverage_type': load_position_leverage_type(position),
                'leverage': to_float(position['leverage']),
                'isolated_wallet_balance': to_float(position.get('isolatedWallet')),
                'cross_wallet_balance': cross_wallet_balance,
                'action': 'update'
            }
    return positions_state


def load_futures_coin_positions_state(account_info: dict, state_data: dict) -> dict:
    balances = {}
    for asset in account_info.get('assets', []):
        balances[asset['asset'].lower()] = to_float(asset['crossWalletBalance'])
    positions_state = {}
    for position in account_info.get('positions', []):
        if position['positionSide'].upper() == BinancePositionSideMode.BOTH:
            symbol = position['symbol'].lower()
            volume = to_float(position['positionAmt'])
            side = load_position_side_by_volume(volume)
            entry_price = to_float(position['entryPrice'])
            _unrealised_pnl = to_float(position['unrealizedProfit'])
            mark_price = BinanceFinFactory.calc_mark_price(
                volume, entry_price, _unrealised_pnl,
                schema=OrderSchema.futures_coin, symbol=symbol, side=side,
            )
            try:
                wallet_asset = state_data.get(symbol, {}).get('pair', [])[0].lower()
                cross_wallet_balance = balances.get(wallet_asset)
            except IndexError:
                cross_wallet_balance = None
            positions_state[symbol] = {
                'symbol': symbol,
                'volume': volume,
                'side': side,
                'entry_price': entry_price,
                'mark_price': mark_price,
                'leverage_type': load_position_leverage_type(position),
                'leverage': to_float(position['leverage']),
                'isolated_wallet_balance': to_float(position.get('isolatedWallet')),
                'cross_wallet_balance': cross_wallet_balance,
                'action': 'update'
            }
    return positions_state


def load_exchange_position(raw_data: dict, schema: str, mark_price: float) -> dict:
    symbol = raw_data.get('symbol')
    volume = to_float(raw_data.get('volume'))
    entry_price = to_float(raw_data.get('entry_price'))
    side = raw_data.get('side')
    mark_price = to_float(mark_price)
    now = datetime.now()
    data = {
        'time': now,
        'schema': schema.lower(),
        'symbol': symbol,
        'side': side,
        'volume': volume,
        'entry_price': entry_price,
        'mark_price': mark_price,
        'unrealised_pnl': BinanceFinFactory.calc_unrealised_pnl_by_side(
            volume=volume, entry_price=entry_price, mark_price=mark_price, side=side
        ),
        'leverage_type': raw_data.get('leverage_type'),
        'leverage': to_float(raw_data.get('leverage')),
        'liquidation_price': to_float(raw_data.get('liquidation_price')),
        }
    return data


def load_margin2_position(raw_data: dict, schema: str, mark_price: float) -> dict:
    return load_exchange_position(raw_data, schema, mark_price)


def load_futures_position(raw_data: dict, schema: str) -> dict:
    now = datetime.now()
    data = {
        'time': now,
        'schema': schema.lower(),
        'symbol': raw_data.get('symbol'),
        'side': load_position_side_by_volume(to_float(raw_data.get('positionAmt'))),
        'volume': to_float(raw_data.get('positionAmt')),
        'entry_price': to_float(raw_data.get('entryPrice')),
        'mark_price': to_float(raw_data.get('markPrice')),
        'unrealised_pnl': to_float(raw_data.get('unRealizedProfit')),
        'leverage_type': raw_data.get('marginType'),
        'leverage': to_float(raw_data.get('leverage')),
        'liquidation_price': to_float(raw_data.get('liquidationPrice')),
        }
    return data


def load_futures_coin_position(raw_data: dict, schema: str) -> dict:
    return load_futures_position(raw_data, schema)


def load_exchange_position_list(raw_data: dict, schema: str, symbol_list: list) -> list:
    symbols_mark_price = {
        symbol.get('symbol', '').lower(): to_float(symbol.get('lastPrice')) for symbol in symbol_list
    }
    return [load_exchange_position(v, schema, symbols_mark_price.get(v.get('symbol'))) for k, v in raw_data.items()]


def load_margin2_position_list(raw_data: dict, schema: str, symbol_list: list) -> list:
    return load_exchange_position_list(raw_data, schema, symbol_list)


def load_futures_position_list(raw_data: list, schema: str) -> list:
    return [load_futures_position(data, schema) for data in raw_data if to_float(data.get('positionAmt')) != 0]


def load_futures_coin_position_list(raw_data: list, schema: str) -> list:
    return load_futures_position_list(raw_data, schema)


def load_exchange_position_ws_data(
        raw_data: dict, position_state: dict, state_data: Optional[dict], exchange_rates: dict) -> dict:
    side = position_state['side']
    volume = to_float(position_state['volume'])
    mark_price = to_float(raw_data.get('c'))
    entry_price = to_float(position_state['entry_price'])
    unrealised_pnl = BinanceFinFactory.calc_unrealised_pnl_by_side(
        side=side, volume=volume, mark_price=mark_price, entry_price=entry_price
    )
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        's': raw_data['s'].lower(),
        'sd': side,
        'vl': volume,
        'ep': entry_price,
        'mp': mark_price,
        'upnl': load_ws_position_unrealised_pnl(unrealised_pnl, state_data, exchange_rates),
        'lvrp': position_state['leverage_type'],
        'lvr': to_float(position_state['leverage']),
        'lp': None,
        'act': 'update'
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


def load_ws_position_unrealised_pnl(base: float, state_data: Optional[dict], exchange_rates: dict) -> dict:
    btc_value = None
    usd_value = None
    unrealised_pnl = {
        'base': base,
        'usd': usd_value,
        'btc': btc_value,
    }
    if isinstance(state_data, dict) and (pair := state_data.get('pair', [])):
        quote_asset = pair[1]
        usd_value = to_usd(base, quote_asset, exchange_rates, state_data.get('expiration', None))
        unrealised_pnl['usd'] = usd_value
        unrealised_pnl['btc'] = to_btc(usd_value, exchange_rates)
    return unrealised_pnl


def to_usd(base: float, asset: str, exchange_rates: dict, expiration: Optional[str]) -> Optional[float]:
    if expiration and (asset_to_usd := exchange_rates.get(f"{asset}{expiration}".lower())):
        pass
    elif asset_to_usd := exchange_rates.get(asset.lower()):
        pass
    else:
        asset_to_usd = 1

    try:
        return base * asset_to_usd
    except TypeError:
        return None


def load_margin2_position_ws_data(
        raw_data: dict, position_state: dict, state_data: Optional[dict], exchange_rates: dict) -> dict:
    data = load_exchange_position_ws_data(raw_data, position_state, state_data, exchange_rates)
    if not data['leverage_type']:
        data['lvrp'] = LeverageType.cross
    if not data['leverage']:
        data['lvr'] = 3
    return data


def load_futures_coin_position_request_leverage(margin_type: str) -> str:
    if margin_type.lower() == LeverageType.isolated:
        return LeverageType.isolated
    return LeverageType.cross


def remap_futures_coin_position_request_data(data: dict) -> dict:
    volume = to_float(data.get('positionAmt'))
    return {
        'E': time2timestamp(datetime.now()),
        'symbol': data.get('symbol'),
        'volume': volume,
        'side': load_position_side_by_volume(volume),
        'entry_price': to_float(data.get('entryPrice')),
        'mark_price': to_float(data.get('markPrice')),
        'leverage': to_float(data.get('leverage')),
        'leverage_type': load_futures_coin_position_request_leverage(data.get('marginType')),
        'unrealised_pnl': to_float(data.get('unRealizedProfit')),
        'liquidation_price': to_float(data.get('liquidationPrice')),
    }


def symbol2pair(symbol: str) -> str:
    return symbol.split('_')[0]
