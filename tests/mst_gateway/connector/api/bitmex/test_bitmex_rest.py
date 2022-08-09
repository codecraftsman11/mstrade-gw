# pylint: disable=no-self-use
import logging
import pytest
from copy import deepcopy
from schema import Schema
from typing import Union, Optional
from datetime import datetime, timedelta
from mst_gateway.logging import init_logger
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
from mst_gateway.exceptions import ConnectorError
from mst_gateway.connector.api import BUY, SELL, OrderType, OrderSchema, LeverageType, OrderExec, OrderTTL
from tests.mst_gateway.connector import schema as fields
from tests import config as cfg
from .data import order as order_data
from .data import storage as data


BITMEX_SYMBOL = 'XBTUSD'


def rest_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_AUTH_KEYS, [OrderSchema.margin])
    }
    return name_map[name]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


@pytest.fixture(params=['tbitmex'])
def rest(request, _debug) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            state_storage=deepcopy(data.STORAGE_DATA),
            logger=_debug['logger']
    ) as api:
        api.open()
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


@pytest.fixture(params=['tbitmex'])
def rest_compress(request, _debug) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            state_storage=deepcopy(data.STORAGE_DATA),
            logger=_debug['logger']
    ) as api:
        api.open(compress=True)
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


@pytest.fixture(params=['tbitmex'])
def rest_keepalive(request, _debug) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            state_storage=deepcopy(data.STORAGE_DATA),
            logger=_debug['logger']
    ) as api:
        api.open(keepalive=True)
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


@pytest.fixture(params=['tbitmex'])
def rest_keepalive_compress(request) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            state_storage=deepcopy(data.STORAGE_DATA)
    ) as api:
        api.open(keepalive=True, compress=True)
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


def get_order_price(rest: BitmexRestApi, schema: str,
                    symbol: str, side: int, order_type: str = order_data.DEFAULT_ORDER_TYPE) -> Optional[float]:
    price = None
    if order_type == OrderType.market:
        return price
    symbol = rest.get_symbol(schema=schema, symbol=symbol)
    if side == BUY:
        return round(symbol.get('bid_price') / 1.05, 0)
    return round(symbol.get('ask_price') * 1.05, 0)


def get_order_stop_price(price: float, side):
    if side == BUY:
        return round(price + 2000, 0)
    return round(price - 2000, 0)


def get_symbol(schema: str) -> Optional[str]:
    if schema == OrderSchema.margin:
        return data.SYMBOL
    return None


def get_asset(schema: str) -> Optional[str]:
    if schema == OrderSchema.margin:
        return data.ASSET
    return None


def create_default_order(rest: BitmexRestApi,
                         schema: str, order_type: str = order_data.DEFAULT_ORDER_TYPE, options: dict = None) -> dict:
    price = get_order_price(rest=rest, schema=schema, symbol=order_data.DEFAULT_SYMBOL,
                            side=order_data.DEFAULT_ORDER_SIDE, order_type=order_type)
    options = options if options else order_data.DEFAULT_ORDER_OPTIONS
    order = rest.create_order(
        schema=schema,
        symbol=order_data.DEFAULT_SYMBOL,
        side=order_data.DEFAULT_ORDER_SIDE,
        volume=order_data.DEFAULT_ORDER_VOLUME[schema],
        order_type=order_type,
        price=price,
        options=options
    )
    return order


def clear_stock_order_data(order: dict):
    order.pop('time')
    order.pop('exchange_order_id')
    order.pop('active')
    if order['type'] in (OrderType.market, OrderType.stop_market):
        order.pop('price')


class TestBitmexRestApi:

    @pytest.mark.parametrize(
        'rest', ['tbitmex'],
        indirect=True,
    )
    def test_get_user(self, rest: BitmexRestApi):
        user = rest.get_user()
        user_schema = Schema(fields.USER_FIELDS)
        assert user_schema.validate(user) == user

    @pytest.mark.parametrize(
        'rest, price, face_price, kwargs', [
            ('tbitmex', 2757.02, 0.00275702, {
                'is_quanto': True, 'is_inverse': False, 'multiplier': 100, 'underlying_multiplier': None
            }),
            ('tbitmex', 38492.64, 0.00002598, {
                'is_quanto': False, 'is_inverse': True, 'multiplier': None, 'underlying_multiplier': None
            }),
            ('tbitmex', 0.07164, 0.00000072, {
                'is_quanto': False, 'is_inverse': False, 'multiplier': None, 'underlying_multiplier': 100000
            }),
        ],
        indirect=['rest'],
    )
    def test_calc_face_price(self, rest: BitmexRestApi, price: float, face_price: float, kwargs: dict):
        calc_face_price = BitmexFinFactory.calc_face_price(price, **kwargs)
        assert face_price == calc_face_price

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_quote_bins(self, rest: BitmexRestApi, schema: str):
        quote_bin_schema = Schema(fields.QUOTE_BIN_FIELDS)
        quote_bins = rest.list_quote_bins(schema=schema, symbol=get_symbol(schema))
        for quote_bin in quote_bins:
            assert quote_bin_schema.validate(quote_bin) == quote_bin
        assert len(quote_bins) == 100

    @pytest.mark.parametrize(
        'rest_compress, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest_compress'],
    )
    def test_list_quote_bins_compress(self, rest_compress: BitmexRestApi, schema: str):
        quote_bin_schema = Schema(fields.QUOTE_BIN_FIELDS)
        for quote_bin in rest_compress.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert quote_bin_schema.validate(quote_bin) == quote_bin

    @pytest.mark.parametrize(
        'rest_keepalive, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest_keepalive'],
    )
    def test_list_quote_bins_keepalive(self, rest_keepalive: BitmexRestApi, schema: str):
        quote_bin_schema = Schema(fields.QUOTE_BIN_FIELDS)
        for quote_bin in rest_keepalive.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert quote_bin_schema.validate(quote_bin) == quote_bin

    @pytest.mark.parametrize(
        'rest_keepalive_compress, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest_keepalive_compress'],
    )
    def test_list_quote_bins_keepalive(self, rest_keepalive_compress: BitmexRestApi, schema: str):
        quote_bin_schema = Schema(fields.QUOTE_BIN_FIELDS)
        for quote_bin in rest_keepalive_compress.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert quote_bin_schema.validate(quote_bin) == quote_bin

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_order_book(self, rest: BitmexRestApi, schema: str):
        ob_schema = Schema(fields.ORDER_BOOK_FIELDS)
        ob_items = rest.list_order_book(symbol=order_data.DEFAULT_SYMBOL, schema=schema)
        for ob_item in ob_items:
            assert ob_schema.validate(ob_item) == ob_item

    @pytest.mark.parametrize(
        'rest, schema, side', [
            ('tbitmex', OrderSchema.margin, BUY),
            ('tbitmex', OrderSchema.margin, SELL),
        ],
        indirect=['rest'],
    )
    def test_get_order_book(self, rest: BitmexRestApi, schema: str, side: int):
        ob_schema = Schema(fields.ORDER_BOOK_FIELDS)
        ob_items = rest.get_order_book(schema=schema, symbol=order_data.DEFAULT_SYMBOL, depth=data.DEFAULT_DEPTH,
                                       side=side, min_volume_sell=data.DEFAULT_MIN_VOLUME_SELL,
                                       min_volume_buy=data.DEFAULT_MIN_VOLUME_BUY)
        for ob_item in ob_items:
            assert ob_schema.validate(ob_item) == ob_item

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_trades(self, rest: BitmexRestApi, schema: str):
        tl_schema = Schema(fields.TRADE_FIELDS)
        lt_items = rest.list_trades(schema=OrderSchema.margin, symbol=BITMEX_SYMBOL)
        for lt_item in lt_items:
            assert tl_schema.validate(lt_item) == lt_item

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest']
    )
    def test_get_wallet(self, rest: BitmexRestApi, schema: str):
        wallet = rest.get_wallet(schema=schema)
        assert Schema(fields.WALLET_FIELDS).validate(wallet) == wallet
        if extra_data := wallet['extra_data']:
            assert Schema(fields.WALLET_EXTRA_FIELDS[schema]).validate(extra_data) == extra_data

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_wallet_detail(self, rest: BitmexRestApi, schema: str):
        wallet_detail = rest.get_wallet_detail(schema=schema, asset=data.ASSET)
        assert Schema(fields.WALLET_BALANCE_FIELDS).validate(wallet_detail) == wallet_detail

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_wallet_extra_data(self, rest: BitmexRestApi, schema):
        wallet_extra = rest.get_wallet_extra_data(schema=schema, asset=data.ASSET)
        if wallet_extra:
            assert Schema(fields.WALLET_EXTRA_DATA_FIELDS[schema]).validate(wallet_extra) == wallet_extra

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_ping(self, rest: BitmexRestApi, schema: str):
        assert rest.ping(schema=schema)

    @pytest.mark.parametrize(
        'rest, schemas, expect', [
            ('tbitmex', [OrderSchema.margin], (
                 {
                     OrderSchema.margin: True,
                 },
                 None
            )),
        ],
        indirect=['rest'],
    )
    def test_get_api_key_permissions(self, rest: BitmexRestApi, schemas, expect):
        assert rest.get_api_key_permissions(schemas) == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_assets_balance(self, rest: BitmexRestApi, schema: str):
        assets_balance = rest.get_assets_balance(schema)
        asset_balance_schema = Schema(fields.ASSETS_BALANCE)
        for a, b in assets_balance.items():
            assert asset_balance_schema.validate({a: b}) == {a: b}

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_wallet_transfer(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_transfer(from_wallet='', to_wallet='', asset=get_asset(schema), amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_wallet_borrow(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_borrow(schema=schema, asset=data.ASSET, amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_wallet_repay(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_repay(schema=schema, asset=data.ASSET, amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_symbol(self, rest: BitmexRestApi, schema: str):
        symbol_schema = Schema(fields.SYMBOL_FIELDS)
        symbol = rest.get_symbol(schema=schema, symbol=data.SYMBOL)
        assert symbol_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_symbols(self, rest: BitmexRestApi, schema: str):
        symbol_schema = Schema(fields.SYMBOL_FIELDS)
        for symbol in rest.list_symbols(schema=schema):
            assert symbol_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_load_exchange_symbol_info(self, rest: BitmexRestApi, schema: str):
        exchange_symbol_schema = Schema(fields.EXCHANGE_BITMEX_SYMBOL_INFO_FIELDS[schema])
        exchange_symbols = rest.get_exchange_symbol_info(schema=schema)
        for exchange_symbol in exchange_symbols:
            assert exchange_symbol_schema.validate(exchange_symbol) == exchange_symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_currency_exchange_symbols(self, rest: BitmexRestApi, schema: str):
        currency_exchange_symbol_schema = Schema(fields.CURRENCY_EXCHANGE_SYMBOL_FIELDS)
        symbols_data = rest.currency_exchange_symbols(schema=schema)
        for symbol_data in symbols_data:
            assert currency_exchange_symbol_schema.validate(symbol_data) == symbol_data

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_symbols_currencies(self, rest: BitmexRestApi, schema: str):
        symbol_currency_schema = Schema(fields.SYMBOL_CURRENCY_FIELDS)
        symbols_currencies = rest.get_symbols_currencies(schema=schema)
        for symbol in symbols_currencies.values():
            assert symbol_currency_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_order_commissions(self, rest: BitmexRestApi, schema: str):
        orders_commissions_schema = Schema(fields.ORDER_COMMISSION_FIELDS)
        orders_commissions = rest.list_order_commissions(schema=schema)
        for commission in orders_commissions:
            assert orders_commissions_schema.validate(commission) == commission

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_vip_level(self, rest: BitmexRestApi, schema: str):
        level = rest.get_vip_level(schema)
        assert isinstance(level, str)
        try:
            int_level = int(level)
        except (TypeError, ValueError):
            int_level = None
        assert isinstance(int_level, int)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier', [
            ('tbitmex', OrderSchema.margin, 8, 1)
        ],
        indirect=['rest'],
    )
    def test_get_funding_rates(self, rest: BitmexRestApi,
                               schema: str, period_hour: int, period_multiplier: int):
        funding_rates_schema = Schema(fields.FUNDING_RATE_FIELDS)
        funding_rates = rest.get_funding_rates(schema=schema, symbol=get_symbol(schema), period_hour=period_hour,
                                               period_multiplier=period_multiplier)
        for funding_rate in funding_rates:
            assert funding_rates_schema.validate(funding_rate) == funding_rate
            assert int(funding_rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier', [
            ('tbitmex', OrderSchema.margin, 8, 1)
        ],
        indirect=['rest'],
    )
    def test_list_funding_rates(self, rest: BitmexRestApi,
                                schema: str, period_hour: int, period_multiplier: int):
        funding_rates_schema = Schema(fields.FUNDING_RATE_FIELDS)
        funding_rates = rest.list_funding_rates(schema=schema, period_hour=period_hour,
                                                period_multiplier=period_multiplier)
        for rate in funding_rates:
            assert funding_rates_schema.validate(rate) == rate
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_leverage(self, rest: BitmexRestApi, schema: str):
        resp = rest.get_leverage(schema=schema, symbol=get_symbol(schema))
        assert isinstance(resp, tuple)
        assert resp[0] in (LeverageType.cross, LeverageType.isolated)
        assert isinstance(resp[1], float)

    @pytest.mark.parametrize(
        'rest, schema, leverage_type, leverage, expect', [
            ('tbitmex', OrderSchema.margin, LeverageType.isolated, 90, (LeverageType.isolated, 90)),
            ('tbitmex', OrderSchema.margin, LeverageType.cross, 100, (LeverageType.cross, 100)),
        ],
        indirect=['rest'],
    )
    def test_change_leverage(self, rest: BitmexRestApi, schema: str,
                             leverage_type: str, leverage: Union[float, int], expect: tuple):
        leverage_data = rest.change_leverage(schema=schema, symbol=get_symbol(schema), leverage_type=leverage_type,
                                             leverage=leverage)
        assert leverage_data == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_position_state(self, rest: BitmexRestApi, schema: str):
        positions_state = rest.get_positions_state(schema=schema)
        assert isinstance(positions_state, dict)

    @pytest.mark.parametrize(
        'rest, schema, side, volume, price, wallet_balance, wallet_detail, funding_rate, taker_fee, leverage_type, '
        'leverage, expect', [
            ('tbitmex', OrderSchema.margin, BUY, 100.0, 57000.0, 0.0012, data.WALLET_DATA[OrderSchema.margin],
             0.0001, 0.05, LeverageType.cross, 100, 34060.3729073
             ),
            ('tbitmex', OrderSchema.margin, BUY, 100.0, 57000.0, 0.0012, data.WALLET_DATA[OrderSchema.margin],
             0.0001, 0.05, LeverageType.isolated, 100, 56971.57118598),
        ],
        indirect=['rest'],
    )
    def test_get_liquidation(self, rest: BitmexRestApi, schema: str, side: int, volume: float, price: float,
                             wallet_balance: float, wallet_detail: dict, funding_rate: float, taker_fee: float,
                             leverage_type: str, leverage: Union[float, int], expect: float):
        liquidation_schema = Schema(fields.LIQUIDATION_FIELDS)
        liquidation_data = rest.get_liquidation(schema=schema, symbol=get_symbol(schema), side=side, volume=volume,
                                                price=price, wallet_balance=wallet_balance, wallet_detail=wallet_detail,
                                                taker_fee=taker_fee, leverage_type=leverage_type, leverage=leverage,
                                                funding_rate=funding_rate)
        assert liquidation_schema.validate(liquidation_data) == liquidation_data
        assert liquidation_data['liquidation_price'] == expect


class TestOrderBitmexRestApi:
    @pytest.mark.parametrize(
        'rest, schema, side, order_type, expect', [
            ('tbitmex', OrderSchema.margin, BUY, OrderType.market, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'schema': OrderSchema.margin,
                'side': BUY,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.IOC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, SELL, OrderType.market, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'schema': OrderSchema.margin,
                'side': SELL,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.IOC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, BUY, OrderType.stop_market, {
                'execution': OrderExec.market,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': BUY,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.stop_market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.IOC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, SELL, OrderType.stop_market, {
                'execution': OrderExec.market,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': SELL,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.stop_market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.IOC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, BUY, OrderType.limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': BUY,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.GTC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, SELL, OrderType.limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': SELL,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.GTC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, BUY, OrderType.stop_limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': BUY,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.stop_limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.GTC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
            ('tbitmex', OrderSchema.margin, SELL, OrderType.stop_limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': SELL,
                'stop': 0.0,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.stop_limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.GTC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
        ],
        indirect=['rest'],
    )
    def test_create_order(self, rest: BitmexRestApi, schema: str, side: int, order_type: str, expect: dict):
        symbol = get_symbol(schema)
        price = get_order_price(rest, schema, symbol, side, order_type)
        default_order_data = order_data.DEFAULT_ORDER_OPTIONS
        if order_type in (OrderType.limit, OrderType.stop_limit, OrderType.stop_market):
            if order_type != OrderType.limit:
                stop_price = get_order_stop_price(price, side)
                default_order_data.update({'stop_price': stop_price})
                expect['stop'] = stop_price
            if order_type != OrderType.stop_market:
                expect['price'] = price

        order_schema = Schema(fields.ORDER_FIELDS)
        order = rest.create_order(symbol, schema, side, order_data.DEFAULT_ORDER_VOLUME[schema], order_type, price,
                                  default_order_data)
        assert order_schema.validate(order) == order
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_order(self, rest: BitmexRestApi, schema):
        default_order = create_default_order(rest, schema)
        order_schema = Schema(fields.ORDER_FIELDS)
        order = rest.get_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert order_schema.validate(order) == order
        clear_stock_order_data(order)
        assert order == order_data.DEFAULT_ORDER[schema]
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_orders(self, rest: BitmexRestApi, schema: str):
        default_order = create_default_order(rest, schema)
        order_schema = Schema(fields.ORDER_FIELDS)
        orders = rest.list_orders(schema, default_order['symbol'])
        for order in orders:
            assert order_schema.validate(order) == order
        clear_stock_order_data(orders[0])
        assert orders[0] == order_data.DEFAULT_ORDER[schema]
        rest.cancel_all_orders(schema)


    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tbitmex', OrderSchema.margin, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin] * 2,
                'schema': OrderSchema.margin,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                'stop': 0.0,
                'symbol': order_data.DEFAULT_SYMBOL,
                'system_symbol': order_data.DEFAULT_SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin] * 2,
                'ttl': OrderTTL.IOC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Submitted via API."
            }),
        ],
        indirect=['rest'],
    )
    def test_bitmex_rest_update_order(self, rest: BitmexRestApi, schema: str, expect: dict):
        default_order = create_default_order(rest, schema)
        order_schema = Schema(fields.ORDER_FIELDS)
        order = rest.update_order(default_order['exchange_order_id'], default_order['symbol'], schema,
                                  side=order_data.DEFAULT_ORDER_OPPOSITE_SIDE, volume=default_order['volume'] * 2,
                                  options=order_data.DEFAULT_ORDER_OPTIONS)
        assert order_schema.validate(order) == order
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)
        rest.close_all_orders(order['symbol'], schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tbitmex', OrderSchema.margin, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin,
                'side': order_data.DEFAULT_ORDER_SIDE,
                'stop': 0.0,
                'symbol': order_data.DEFAULT_SYMBOL,
                'system_symbol': order_data.DEFAULT_SYSTEM_SYMBOL,
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin],
                'ttl': OrderTTL.GTC,
                'iceberg_volume': 0.0,
                'is_iceberg': False,
                'is_passive': False,
                'comments': "Canceled: Canceled via API.\nSubmitted via API."
            }),
        ],
        indirect=['rest'],
    )
    def test_cancel_order(self, rest: BitmexRestApi, schema: str, expect: dict):
        default_order = create_default_order(rest, schema)
        order_schema = Schema(fields.ORDER_FIELDS)
        order = rest.cancel_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert order_schema.validate(order) == order
        clear_stock_order_data(order)
        assert order == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_cancel_all_orders(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema)
        assert rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_close_order(self, rest: BitmexRestApi, schema: str):
        default_order = create_default_order(rest, schema)
        assert rest.close_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_close_all_orders(self, rest: BitmexRestApi, schema: str):
        default_order = create_default_order(rest, schema)
        assert rest.close_all_orders(default_order['symbol'], schema)
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_get_position(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema, order_type=OrderType.market)
        position_schema = Schema(fields.POSITION_FIELDS)
        position = rest.get_position(schema=schema, symbol=order_data.DEFAULT_SYMBOL)
        assert position_schema.validate(position) == position
        rest.cancel_all_orders(schema)
        rest.close_all_orders(schema=schema, symbol=order_data.DEFAULT_SYMBOL)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin)],
        indirect=['rest'],
    )
    def test_list_position(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema, order_type=OrderType.market)
        position_schema = Schema(fields.POSITION_FIELDS)
        positions = rest.list_positions(schema=schema)
        for position in positions:
            assert position_schema.validate(position) == position
        rest.cancel_all_orders(schema)
        rest.close_all_orders(schema=schema, symbol=order_data.DEFAULT_SYMBOL)
