from datetime import datetime, timezone
from typing import Union, Optional
from mst_gateway.connector import api
from mst_gateway.calculator import BinanceFinFactory
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
    data = {
        'time': symbol_time,
        'symbol': symbol,
        'schema': schema,
        'price': price,
        'price24': price24,
        'delta': delta(price, price24),
        'bid_price': to_float(raw_data.get('bidPrice')),
        'ask_price': to_float(raw_data.get('askPrice')),
        'volume24': to_float(raw_data.get('volume')),
        'mark_price': price,
        'high_price': to_float(raw_data.get('highPrice')),
        'low_price': to_float(raw_data.get('lowPrice')),
        'funding_rate': None
    }
    if isinstance(state_data, dict):
        face_price_data = state_data.get('extra', {}).get('face_price_data', {})
        face_price = BinanceFinFactory.calc_face_price(price, schema=schema, **face_price_data)
        data.update({
            'face_price': face_price,
            'expiration': state_data.get('expiration'),
            'expiration_date': state_data.get('expiration_date'),
            'pair': state_data.get('pair'),
            'tick': state_data.get('tick'),
            'volume_tick': state_data.get('volume_tick'),
            'system_symbol': state_data.get('system_symbol'),
            'created': to_date(state_data.get('created')),
            'max_leverage': state_data.get('max_leverage'),
            'wallet_asset': state_data.get('wallet_asset'),
        })
    return data


def load_futures_symbol_data(schema: str, raw_data: Optional[dict], state_data: Optional[dict]) -> dict:
    if data := load_symbol_data(schema, raw_data, state_data):
        data.update({
            'mark_price': to_float(raw_data.get('markPrice')),
            'funding_rate': load_funding_rate(raw_data.get('lastFundingRate'))
        })
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
                'base_asset': d.get('baseAsset'),
                'quote_asset': d.get('quoteAsset'),
                'system_base_asset': system_base_asset,
                'system_quote_asset': system_quote_asset,
                'base_asset_precision': d.get('baseAssetPrecision'),
                'quote_asset_precision': d.get('quoteAssetPrecision'),
                'expiration': None,
                'expiration_date': None,
                'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                'tick': tick,
                'volume_tick': volume_tick,
                'max_leverage': None,
                'wallet_asset': None,
                'extra': {}
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
            max_leverage = 100.0
            extra = {}
            if face_price_data := d.get('contractSize'):
                extra['face_price_data'] = {'contract_size': face_price_data}
            leverage_brackets = leverage_data.get(d['symbol'].lower(), [])
            extra['leverage_brackets'] = leverage_brackets
            if leverage_brackets and leverage_brackets[0].get('initial_leverage'):
                max_leverage = to_float(leverage_brackets[0]['initial_leverage'])

            symbol_list.append(
                {
                    'symbol': d.get('symbol'),
                    'system_symbol': system_symbol.lower(),
                    'base_asset': d.get('baseAsset'),
                    'quote_asset': d.get('quoteAsset'),
                    'system_base_asset': system_base_asset,
                    'system_quote_asset': system_quote_asset,
                    'base_asset_precision': d.get('baseAssetPrecision'),
                    'quote_asset_precision': d.get('quotePrecision'),
                    'expiration': expiration,
                    'expiration_date': load_futures_symbol_expiration_date(expiration),
                    'pair': [d.get('baseAsset').upper(), d.get('quoteAsset').upper()],
                    'system_pair': [system_base_asset.upper(), system_quote_asset.upper()],
                    'schema': schema.lower(),
                    'tick': tick,
                    'volume_tick': volume_tick,
                    'max_leverage': max_leverage,
                    'wallet_asset': d.get('marginAsset').upper(),
                    'extra': extra
                }
            )
    return symbol_list


def load_futures_exchange_symbol_info(raw_data: list, leverage_data: dict) -> list:
    return _load_futures_exchange_symbol_info(raw_data, leverage_data, OrderSchema.margin, 'status')


def load_futures_coin_exchange_symbol_info(raw_data: list, leverage_data: dict) -> list:
    return _load_futures_exchange_symbol_info(raw_data, leverage_data, OrderSchema.margin_coin, 'contractStatus')


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
        'volume': to_float(raw_data.get('qty')),
        'side': load_order_side(raw_data.get('isBuyerMaker'))
    }
    if isinstance(state_data, dict):
        data.update({
            'symbol': state_data.get('symbol'),
            'system_symbol': state_data.get('system_symbol'),
            'schema': state_data.get('schema')
        })
    return data


def load_order_side(order_side: Union[bool, str]) -> int:
    if isinstance(order_side, bool):
        if order_side:
            return api.BUY
        else:
            return api.SELL
    if isinstance(order_side, str):
        if order_side == var.BINANCE_ORDER_SIDE_SELL:
            return api.SELL
        else:
            return api.BUY


def store_order_side(side: int) -> str:
    if side:
        return var.BINANCE_ORDER_SIDE_SELL
    return var.BINANCE_ORDER_SIDE_BUY


def store_order_type(order_type: str, schema: str) -> str:
    converter = BinanceOrderTypeConverter
    return converter.store_type(order_type, schema)


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


def load_order_passive(ttl: str) -> bool:
    return ttl.upper() == 'GTX'


def _load_price_and_filled_volume(fills: list) -> dict:
    filled_volume = 0.0
    amount = 0.0
    for fill in fills:
        qty = to_float(fill.get('qty'))
        price = to_float(fill.get('price'))
        amount += price * qty
        filled_volume += qty
    try:
        entry_price = amount / filled_volume
    except ZeroDivisionError:
        entry_price = 0.0
    data = {
        "price": round(entry_price, 8),
        "filled_volume": round(filled_volume, 8)
    }
    return data


def load_order_data(schema: str, raw_data: dict, state_data: Optional[dict], payload: dict = None) -> dict:
    _time_field = raw_data.get('time') or raw_data.get('transactTime') or raw_data.get('updateTime')
    _time = to_date(_time_field) or datetime.now()
    order_type = raw_data.get('type') or payload.get('type')
    order_type_and_exec = load_order_type_and_exec(schema, order_type.upper())
    iceberg_volume = to_float(raw_data.get('icebergQty', 0.0))
    data = {
        'time': _time,
        'exchange_order_id': str(raw_data.get('orderId')),
        'symbol': raw_data.get('symbol'),
        'schema': schema,
        'volume': to_float(raw_data.get('origQty') or payload.get('quantity')),
        'filled_volume': to_float(raw_data.get('executedQty')),
        'stop': to_float(raw_data.get('stopPrice') or payload.get('stopPrice')),
        'side': load_order_side(raw_data.get('side') or payload.get('side')),
        'price': to_float(raw_data.get('price') or payload.get('price')),
        'active': raw_data.get('status') != "NEW",
        'ttl': var.BINANCE_ORDER_TTL_MAP.get(raw_data.get('timeInForce') or payload.get('timeInForce')),
        'is_iceberg': bool(iceberg_volume),
        'iceberg_volume': iceberg_volume,
        'is_passive': load_order_passive(raw_data.get('timeInForce') or payload.get('timeInForce')),
        'comments': None,
        **order_type_and_exec
    }
    if fills := raw_data.get('fills'):
        data.update(
            _load_price_and_filled_volume(fills)
        )
    if isinstance(state_data, dict):
        data.update({
            'system_symbol': state_data.get('system_symbol'),
        })
    return data


def load_user_data(raw_data: dict) -> dict:
    data = {
        'id': str(raw_data.get('address')).lower()
    }
    return data


def load_api_key_permissions(raw_data: dict, schemas: iter) -> dict:
    schema_handlers = {
        OrderSchema.exchange: raw_data.get('enableSpotAndMarginTrading', False),
        OrderSchema.margin_cross: raw_data.get('enableSpotAndMarginTrading', False),
        OrderSchema.margin_isolated: raw_data.get('enableSpotAndMarginTrading', False),
        OrderSchema.margin: raw_data.get('enableFutures', False),
        OrderSchema.margin_coin: raw_data.get('enableFutures', False),
    }
    return {schema: schema_handlers.get(schema, False) for schema in schemas}


def load_spot_wallet_data(raw_data: dict) -> dict:
    balances, _ = _spot_balance_data(raw_data.get('balances'))
    return {
        'balances': balances,
        'extra_data': None
    }


def load_ws_spot_wallet_data(raw_data: dict) -> dict:
    balances, _ = _spot_ws_balance_data(raw_data.get('balances'))
    return {
        'bls': balances,
        'ex': None
    }


def load_spot_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    if not raw_data.get('balances'):
        return _mock_balance_data(asset)
    for a in raw_data.get('balances'):
        if a.get('asset', '').upper() == asset.upper():
            return _spot_balance_data([a])[0][0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_cross_wallet_data(raw_data: dict) -> dict:
    balances, extra_balances = _margin_cross_balance_data(raw_data.get('userAssets'))
    return {
        'balances': balances,
        'extra_data': {
            'trade_enabled': raw_data.get('tradeEnabled'),
            'transfer_enabled': raw_data.get('transferEnabled'),
            'borrow_enabled': raw_data.get('borrowEnabled'),
            'margin_level': to_float(raw_data.get('marginLevel')),
            'balances': extra_balances,
        }
    }


def load_ws_margin_cross_wallet_data(raw_data: dict) -> dict:
    balances, extra_balances = _margin_cross_ws_balance_data(raw_data.get('userAssets'))
    return {
        'bls': balances,
        'ex': {
            'tre': raw_data.get('tradeEnabled'),
            'trse': raw_data.get('transferEnabled'),
            'bore': raw_data.get('borrowEnabled'),
            'mlvl': raw_data.get('marginLevel'),
            'bls': extra_balances,
        }
    }


def load_margin_isolated_wallet_data(raw_data: dict) -> dict:
    balances = margin_isolated_balance_data(raw_data.get('assets'))
    return {
        'balances': balances
    }


def load_margin_cross_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('userAssets'):
        if a.get('asset', '').upper() == asset.upper():
            return _margin_cross_balance_data(
                balances=[a]
            )[0][0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_margin_cross_wallet_extra_data(raw_data: dict, asset: str, max_borrow: Optional[dict],
                                        interest_rate: float) -> dict:
    data = {}
    for a in raw_data.get('userAssets'):
        if a.get('asset', '').upper() == asset.upper():
            data['currency'] = asset.upper()
            data['interest'] = to_float(a.get('interest'))
            data['borrowed'] = to_float(a.get('borrowed'))
            data['interest_rate'] = interest_rate
            data['available_borrow'] = _margin_max_borrow(max_borrow)
    return data


def get_vip(data: dict) -> str:
    return str(data.get('feeTier', 0))


def get_interest_rate(raw_data: dict, vip_level: str, asset: str):
    _h1_rate = None
    for rate in raw_data['data']:
        if rate.get('assetName', '').upper() == asset.upper():
            for spec in rate['specs']:
                if str(spec.get('vipLevel')) == vip_level:
                    _r = to_float(spec.get('dailyInterestRate')) or 0
                    _h1_rate = round(_r * 100 / 24, 8)
                    break
    return _h1_rate


def _update_futures_extra_balances(balances: list, cross_collaterals: list) -> list:
    for balance in balances:
        for collateral in cross_collaterals:
            if balance['currency'] == collateral['loanCoin']:
                balance['borrowed'] += to_float(collateral['loanAmount']) or 0.0
                balance['interest'] += to_float(collateral['interest']) or 0.0
    return balances


def load_futures_wallet_data(raw_data: dict, cross_collaterals: list) -> dict:
    balances, extra_balances = _futures_balance_data(raw_data.get('assets'))
    _update_futures_extra_balances(extra_balances, cross_collaterals)
    return {
        'balances': balances,
        'extra_data': {
            'trade_enabled': raw_data.get('canTrade'),
            'balances': extra_balances,
        }
    }


def _update_ws_futures_extra_balances(balances: list, cross_collaterals: list) -> list:
    for balance in balances:
        for collateral in cross_collaterals:
            if balance['cur'] == collateral['loanCoin']:
                balance['bor'] += to_float(collateral['loanAmount']) or 0.0
                balance['ist'] += to_float(collateral['interest']) or 0.0
    return balances


def load_ws_futures_wallet_data(raw_data: dict, cross_collaterals: list) -> dict:
    balances, extra_balances = _ws_futures_balance_data(raw_data.get('assets'))
    _update_ws_futures_extra_balances(balances, cross_collaterals)
    return {
        'bls': balances,
        'ex': {
            'tre': raw_data.get('canTrade'),
            'bls': extra_balances
        }
    }


def load_futures_coin_wallet_data(raw_data: dict) -> dict:
    balances, _ = _futures_coin_balance_data(raw_data.get('assets'))
    return {
        'balances': balances,
        'extra_data': {
            'trade_enabled': raw_data.get('canTrade'),
        }
    }


def load_ws_futures_coin_wallet_data(raw_data: dict) -> dict:
    balances, _ = _ws_futures_coin_balance_data(raw_data.get('assets'))
    return {
        'bls': balances,
        'ex': {
            'tre': raw_data.get('canTrade'),
        }
    }


def load_futures_wallet_detail_data(raw_data: dict, asset: str) -> dict:
    for a in raw_data.get('assets'):
        if a.get('asset', '').upper() == asset.upper():
            return _futures_balance_data([a])[0][0]
    raise ConnectorError(f"Invalid asset {asset}.")


def load_futures_wallet_extra_data(cross_collaterals_data: dict, collateral_configs: list, asset: str) -> dict:
    """ combining cross_collaterals data and collateral_configs data """

    collaterals = {}
    for collateral_coin in cross_collaterals_data.get('crossCollaterals', []):
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
    return {
        'currency': asset.upper(),
        'interest': to_float(cross_collaterals_data.get('totalInterest')),
        'borrowed': to_float(cross_collaterals_data.get('totalBorrowed')),
        'cross_collaterals': cross_collaterals
    }


def load_margin_cross_collaterals_data(cross_collaterals: dict) -> list:
    data = [{
        'collateral_currency': cross.get('collateralCoin'),
        'borrowed_currency': cross.get('loanCoin'),
        'locked': to_float(cross.get('locked')),
        'borrowed': to_float(cross.get('loanAmount')),
    } for cross in cross_collaterals.get('crossCollaterals', [])]
    return data


def load_exchange_asset_balance(raw_data: dict) -> dict:
    balances = {}
    for balance in raw_data['balances']:
        balances[balance.get('asset', '').lower()] = to_float(balance.get('free', 0))
    return balances


def load_margin_cross_asset_balance(raw_data: dict) -> dict:
    balances = {}
    for balance in raw_data['userAssets']:
        balances[balance.get('asset', '').lower()] = to_float(balance.get('free', 0))
    return balances


def load_futures_asset_balance(raw_data: list) -> dict:
    balances = {}
    for balance in raw_data:
        balances[balance.get('asset', '').lower()] = to_float(balance.get('balance', 0))
    return balances


def load_futures_coin_asset_balance(raw_data: list) -> dict:
    return load_futures_asset_balance(raw_data)


def _update_state_ws_spot_balances(balances: list, state_balances: dict) -> list:
    """
    Update wallet state data by incoming message
    """
    _balances = []
    for asset in balances:
        state_balances[asset['cur'].lower()] = asset
    return list(state_balances.values())


def ws_spot_wallet(raw_data: dict, state_data: dict) -> dict:
    """
    BinanceWalletSerializer
    """
    data, _ = _spot_ws_balance_data(raw_data.get('B', []))
    balances = _update_state_ws_spot_balances(data, state_data['bls'])
    return {
        'bls': balances,
        'ex': None,
    }


def _load_ws_margin_cross_balances(raw_data: dict, state_data: dict):
    """
    Update wallet state data by incoming message
    """
    balances = state_data['bls']
    extra_balances = state_data['ex']['bls']
    for b in raw_data.get('B', []):
        _currency = b['a'].lower()
        _free = to_float(b['f'])
        _locked = to_float(b['l'])
        _balance = round(_free + _locked, 8)
        _withdraw_balance = balances[_currency]['wbl']
        balances[_currency] = {
            'cur': b['a'],
            'bl': _balance,
            'wbl': _withdraw_balance,
            'upnl': 0,
            'mbl': _balance,
            'mm': 0,
            'im': _locked,
            'am': _free,
            't': 'hold',
        }
    return list(balances.values()), list(extra_balances.values())


def ws_margin_cross_wallet(raw_data: dict, state_data: dict) -> dict:
    """
    BinanceWalletSerializer
    """
    balances, extra_balances = _load_ws_margin_cross_balances(raw_data, state_data)
    return {
        'bls': balances,
        'ex': {
            'tre': state_data['ex'].get('tre'),
            'trse': state_data['ex'].get('trse'),
            'bore': state_data['ex'].get('bore'),
            'mlvl': state_data['ex'].get('mlvl'),
            'bls': extra_balances,
        }
    }


def _load_ws_futures_balances(raw_data: dict, state_data: dict):
    """
    Update wallet state data by incoming message
    """
    balances = state_data['bls']
    extra_balances = state_data['ex'].get('bls', {})

    positions_upnl = {}
    for position in raw_data.get('a', {}).get('P', []):
        positions_upnl.setdefault(position['ma'].lower(), 0)
        positions_upnl[position['ma'].lower()] += to_float(position['up'])

    for b in raw_data.get('a', {}).get('B', []):
        _currency = b['a'].lower()
        _balance = to_float(b['wb'])
        _unrealised_pnl = positions_upnl.get(_currency) or 0
        _margin_balance = _balance + _unrealised_pnl
        _maint_margin = balances[_currency]['mm']
        _init_margin = balances[_currency]['im']
        balances[_currency] = {
            'cur': b['a'],
            'bl': _balance,
            'wbl': _margin_balance - _init_margin,
            'upnl': _unrealised_pnl,
            'mbl': _margin_balance,
            'mm': _maint_margin,
            'im': _init_margin,
            'am': _margin_balance - _init_margin,
            't': to_wallet_state_type(_unrealised_pnl)
        }
    return list(balances.values()), list(extra_balances.values())


def ws_futures_wallet(raw_data: dict, state_data: dict) -> dict:
    """
    BinanceWalletSerializer
    """
    balances, extra_balances = _load_ws_futures_balances(raw_data, state_data)
    return {
        'bls': balances,
        'ex': {
            'tre': state_data['ex'].get('tre'),
            'bls': extra_balances,
        },
    }


def ws_futures_coin_wallet(raw_data: dict, state_data: dict) -> dict:
    """
    BinanceWalletSerializer
    """
    balances, _ = _load_ws_futures_balances(raw_data, state_data)
    return {
        'bls': balances,
        'ex': {
            'tre': state_data['ex'].get('tre')
        },
    }


def _mock_balance_data(asset) -> dict:
    return {
        'currency': asset.upper(),
        'balance': 0.0,
        'withdraw_balance': 0.0,
        'unrealised_pnl': 0.0,
        'margin_balance': 0.0,
        'maint_margin': 0.0,
        'init_margin': 0.0,
        'available_margin': 0.0,
        'type': to_wallet_state_type(0),
    }


def _spot_balance_data(balances: list):
    """
    used: load_spot_wallet_data
    """
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


def _spot_ws_balance_data(balances: list):
    """
    Load spot data from rest to ws structure
    used: load_ws_spot_wallet_data
    used: ws_spot_wallet
    """
    result = []
    for b in balances:
        asset = b['asset'] if 'asset' in b else b['a']
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


def _margin_cross_balance_data(balances: list):
    """
    used: load_margin_cross_wallet_data
    """
    result = []
    extra_result = []
    for b in balances:
        wd, ex_wd = _get_margin_cross_balance(b)
        result.append(wd)
        extra_result.append(ex_wd)
    return result, extra_result


def _get_margin_cross_balance(balance: dict):
    """
    rest: Parse margin_cross balance data
    """
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


def _margin_cross_ws_balance_data(balances: list):
    """
    used: load_ws_margin_cross_wallet_data
    """
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
            'ist': interest,
        })
    return result, extra_result


def margin_isolated_balance_data(balances: list, max_borrow: dict = None, interest_rate: dict = None):
    result = list()
    max_borrow_base_asset = _margin_max_borrow(max_borrow.get('base_asset')) if max_borrow else None
    max_borrow_quote_asset = _margin_max_borrow(max_borrow.get('quote_asset')) if max_borrow else None
    interest_rate_base_asset = interest_rate.get('base_asset') if max_borrow else None
    interest_rate_quote_asset = interest_rate.get('quote_asset') if max_borrow else None
    for b in balances:
        try:
            base_asset, _ = _get_margin_cross_balance(b['baseAsset'])
            quote_asset, _ = _get_margin_cross_balance(b['quoteAsset'])
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
    """
    used: load_futures_wallet_data
    """
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
    """
    used: load_ws_futures_wallet_data
    """
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


def _futures_coin_balance_data(balances: list):
    """
    used: load_futures_coin_wallet_data
    """
    result = []
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
            'type': to_wallet_state_type(to_float(b['maintMargin']))
        })
    return result, None


def _ws_futures_coin_balance_data(balances: list):
    """
    used: load_ws_futures_coin_wallet_data
    """
    result = []
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
            't': to_wallet_state_type(to_float(b['maintMargin']))
        })
    return result, None


def load_futures_leverage_brackets_as_dict(data: list) -> dict:
    result = {}
    for d in data:
        result.setdefault(d['symbol'].lower(), [])
        for bracket in d.get('brackets', []):
            result[d['symbol'].lower()].append({
                'bracket': bracket['bracket'],
                'initial_leverage': to_float(bracket['initialLeverage']),
                'notional_cap': to_float(bracket['notionalCap']),
                'notional_floor': to_float(bracket['notionalFloor']),
                'maint_margin_ratio': to_float(bracket['maintMarginRatio']),
                'cum': to_float(bracket['cum'])
            })
    return result


def load_futures_coin_leverage_brackets_as_dict(data: list) -> dict:
    result = {}
    for d in data:
        result.setdefault(d['symbol'].lower(), [])
        for bracket in d.get('brackets', []):
            result[d['symbol'].lower()].append({
                'bracket': bracket['bracket'],
                'initial_leverage': to_float(bracket['initialLeverage']),
                'qty_cap': to_float(bracket['qtyCap']),
                'qty_floor': to_float(bracket['qtyFloor']),
                'maint_margin_ratio': to_float(bracket['maintMarginRatio']),
                'cum': to_float(bracket['cum'])
            })
    return result


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
            'type': f"VIP{commission['level']}",
        } for commission in raw_data['data']
    ]


def to_exchange_asset(asset: str, schema: str):
    if asset == 'usd' and schema != OrderSchema.margin_coin:
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
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        's': symbol,
        'p': price,
        'p24': price24,
        'dt': delta(price, price24),
        'bip': to_float(raw_data.get('b')),
        'asp': to_float(raw_data.get('a')),
        'v24': to_float(raw_data.get('v')),
        'mp': to_float(raw_data.get('c')),
        'hip': to_float(raw_data.get("h")),
        'lop': to_float(raw_data.get('l')),
        'fr': None
    }
    if isinstance(state_data, dict):
        face_price_data = state_data.get('extra', {}).get('face_price_data', {})
        face_price = BinanceFinFactory.calc_face_price(price, schema=schema, **face_price_data)
        data.update({
            'fp': face_price,
            'exp': state_data.get('expiration'),
            'expd': state_data.get('expiration_date'),
            'pa': state_data.get('pair'),
            'tck': state_data.get('tick'),
            'vt': state_data.get('volume_tick'),
            'ss': state_data.get('system_symbol'),
            'crt': to_iso_datetime(to_date(state_data.get('created'))),
            'mlvr': state_data.get('max_leverage'),
            'wa': state_data.get('wallet_asset'),
        })
    return data


def load_futures_symbol_ws_data(schema: str, raw_data: dict, state_data: Optional[dict]) -> dict:
    if data := load_symbol_ws_data(schema, raw_data, state_data):
        data.update({
            'mp': to_float(raw_data.get('mp')),
            'fr': load_funding_rate(raw_data.get('fr'))
        })
    return data


def load_funding_rate(value: str) -> float:
    value = to_float(value)
    return value * 100 if value else value


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
    if raw_data.get('ap'):  # margin
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
    exchange_order_type = store_order_type(order_type, schema)
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

    if options.get('is_passive') and schema in [api.OrderSchema.margin_coin, api.OrderSchema.margin]:
        new_options['ttl'] = var.PARAMETER_NAMES_MAP.get('GTX')
    if 'stop_price' in options:
        new_options['stop_price'] = options['stop_price']
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


def load_futures_position_ws_data(raw_data: dict, position_state_data: dict, state_data: Optional[dict]) -> dict:
    data = {
        'tm': to_iso_datetime(raw_data.get('E')),
        's': position_state_data['symbol'].lower(),
        'sd': position_state_data['side'],
        'vl': position_state_data['volume'],
        'ep': position_state_data['entry_price'],
        'mp': position_state_data['mark_price'],
        'upnl': position_state_data['unrealised_pnl'],
        'lvrp': position_state_data['leverage_type'],
        'lvr': position_state_data['leverage'],
        'lp': position_state_data['liquidation_price'],
        'act': position_state_data['action']
    }
    if isinstance(state_data, dict):
        data.update({
            'ss': state_data.get('system_symbol')
        })
    return data


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
            contract_size = state_data.get(
                symbol, {}).get('extra', {}).get('face_price_data', {}).get('contract_size')
            mark_price = BinanceFinFactory.calc_mark_price(
                volume, entry_price, _unrealised_pnl,
                schema=OrderSchema.margin_coin, symbol=symbol, side=side, contract_size=contract_size
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


def load_futures_position_list(raw_data: list, schema: str) -> list:
    return [load_futures_position(data, schema) for data in raw_data if to_float(data.get('positionAmt')) != 0]


def load_futures_coin_position_list(raw_data: list, schema: str) -> list:
    return load_futures_position_list(raw_data, schema)


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
