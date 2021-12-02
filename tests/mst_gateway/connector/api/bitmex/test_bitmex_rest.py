# pylint: disable=no-self-use
import pytest
from copy import deepcopy
from typing import Union, Optional
from datetime import datetime, timedelta
from mst_gateway.connector.api.stocks.bitmex import BitmexRestApi
from mst_gateway.exceptions import ConnectorError, RecoverableError
from mst_gateway.connector.api import BUY, SELL, OrderType, OrderSchema, LeverageType, OrderExec
from mst_gateway.connector.api import schema as fields
import tests.config as cfg
from .data import order as order_data
from .data import storage as data


def rest_params(name):
    name_map = {
        'tbitmex': (True, cfg.BITMEX_TESTNET_AUTH_KEYS, [OrderSchema.margin1])
    }
    return name_map[name]


@pytest.fixture(params=['tbitmex'])
def rest(request) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            throttle_limit=90,
            state_storage=deepcopy(data.STORAGE_DATA)
    ) as api:
        api.open()
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


@pytest.fixture(params=['tbitmex'])
def rest_compress(request) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            throttle_limit=30,
            state_storage=deepcopy(data.STORAGE_DATA)
    ) as api:
        api.open(compress=True)
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


@pytest.fixture(params=['tbitmex'])
def rest_keepalive(request) -> BitmexRestApi:
    api_name = request.param
    test, auth, available_schemas = rest_params(api_name)
    with BitmexRestApi(
            name=api_name,
            auth=auth,
            throttle_limit=30,
            state_storage=deepcopy(data.STORAGE_DATA)
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
            throttle_limit=30,
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
        price = symbol.get('bid_price') - 10000
    if side == SELL:
        price = symbol.get('ask_price') + 10000
    return price


def get_symbol(schema: str) -> Optional[str]:
    if schema == OrderSchema.margin1:
        return data.SYMBOL
    return None


def get_asset(schema: str) -> Optional[str]:
    if schema == OrderSchema.margin1:
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
    order.pop('price')
    order.pop('active')


class TestBitmexRestApi:

    @pytest.mark.parametrize(
        'rest', ['tbitmex'],
        indirect=True,
    )
    def test_get_user(self, rest: BitmexRestApi):
        assert fields.data_valid(rest.get_user(), fields.USER_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_symbols(self, rest: BitmexRestApi, schema: str):
        for symbol in rest.list_symbols(schema=schema):
            assert fields.data_valid(symbol, fields.SYMBOL_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_quote_bins(self, rest: BitmexRestApi, schema: str):
        for quote_bin in rest.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert fields.data_valid(quote_bin, fields.QUOTE_BIN_FIELDS)

    @pytest.mark.parametrize(
        'rest_compress, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest_compress'],
    )
    def test_list_quote_bins_compress(self, rest_compress: BitmexRestApi, schema: str):
        for quote_bin in rest_compress.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert fields.data_valid(quote_bin, fields.QUOTE_BIN_FIELDS)

    @pytest.mark.parametrize(
        'rest_keepalive, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest_keepalive'],
    )
    def test_list_quote_bins_keepalive(self, rest_keepalive: BitmexRestApi, schema: str):
        for quote_bin in rest_keepalive.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert fields.data_valid(quote_bin, fields.QUOTE_BIN_FIELDS)

    @pytest.mark.parametrize(
        'rest_keepalive_compress, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest_keepalive_compress'],
    )
    def test_list_quote_bins_keepalive(self, rest_keepalive_compress: BitmexRestApi, schema: str):
        for quote_bin in rest_keepalive_compress.list_quote_bins(schema=schema, symbol=get_symbol(schema)):
            assert fields.data_valid(quote_bin, fields.QUOTE_BIN_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema, side, order_type, expect', [
            ('tbitmex', OrderSchema.margin1, BUY, OrderType.market, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1],
                'schema': OrderSchema.margin1,
                'side': BUY,
                'stop': None,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1]
            }),
            ('tbitmex', OrderSchema.margin1, SELL, OrderType.market, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1],
                'schema': OrderSchema.margin1,
                'side': SELL,
                'stop': None,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1]
            }),
            ('tbitmex', OrderSchema.margin1, BUY, OrderType.limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin1,
                'side': BUY,
                'stop': None,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1]
            }),
            ('tbitmex', OrderSchema.margin1, SELL, OrderType.limit, {
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.margin1,
                'side': SELL,
                'stop': None,
                'symbol': data.SYMBOL,
                'system_symbol': data.SYSTEM_SYMBOL,
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1]
            }),
        ],
        indirect=['rest'],
    )
    def test_create_order(self, rest: BitmexRestApi, schema: str, side: int, order_type: str, expect: dict):
        symbol = get_symbol(schema)
        price = None
        if order_type == OrderType.limit:
            price = get_order_price(rest, schema, symbol, side)
        order = rest.create_order(symbol, schema, side, order_data.DEFAULT_ORDER_VOLUME[schema], order_type, price,
                                  order_data.DEFAULT_ORDER_OPTIONS)
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_order(self, rest: BitmexRestApi, schema):
        default_order = create_default_order(rest, schema)
        order = rest.get_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == order_data.DEFAULT_ORDER[schema]
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_orders(self, rest: BitmexRestApi, schema: str):
        default_order = create_default_order(rest, schema)
        orders = rest.list_orders(schema, default_order['symbol'])
        for order in orders:
            assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(orders[0])
        assert orders[0] == order_data.DEFAULT_ORDER[schema]
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tbitmex', OrderSchema.margin1, {
                'execution': OrderExec.market,
                'filled_volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1] * 2,
                'schema': OrderSchema.margin1,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                'stop': None,
                'symbol': order_data.DEFAULT_SYMBOL,
                'system_symbol': order_data.DEFAULT_SYSTEM_SYMBOL,
                'type': OrderType.market,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.margin1] * 2,
            }),
        ],
        indirect=['rest'],
    )
    def test_bitmex_rest_update_order(self, rest: BitmexRestApi, schema: str, expect: dict):
        default_order = create_default_order(rest, schema)
        order = rest.update_order(default_order['exchange_order_id'], default_order['symbol'], schema,
                                  side=order_data.DEFAULT_ORDER_OPPOSITE_SIDE, volume=default_order['volume'] * 2,
                                  options=order_data.DEFAULT_ORDER_OPTIONS)
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)
        # rest.close_all_orders(order['symbol'], schema) # TODO: enable when bitmex fix his EP

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_cancel_order(self, rest: BitmexRestApi, schema: str):
        default_order = create_default_order(rest, schema)
        order = rest.cancel_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        print(f"{order=}")
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == order_data.DEFAULT_ORDER[schema]

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_cancel_all_orders(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema)
        assert rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_close_order(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(RecoverableError): # TODO: remove it when bitmex fix his EP
            default_order = create_default_order(rest, schema)
            order = rest.close_order(default_order['exchange_order_id'], default_order['symbol'], schema)
            assert order

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_close_all_order(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(RecoverableError): # TODO: enable when bitmex fix his EP
            default_order = create_default_order(rest, schema)
            order = rest.close_all_orders(default_order['exchange_order_id'], default_order['symbol'])
            assert order

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_order_book(self, rest: BitmexRestApi, schema: str):
        ob_items = rest.list_order_book(symbol=order_data.DEFAULT_SYMBOL, schema=schema)
        for ob_item in ob_items:
            assert fields.data_valid(ob_item, fields.ORDER_BOOK_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema, side', [
            ('tbitmex', OrderSchema.margin1, BUY),
            ('tbitmex', OrderSchema.margin1, SELL),
        ],
        indirect=['rest'],
    )
    def test_get_order_book(self, rest: BitmexRestApi, schema: str, side: int):
        ob_items = rest.get_order_book(schema=schema, symbol=order_data.DEFAULT_SYMBOL, depth=data.DEFAULT_DEPTH,
                                      side=side, min_volume_sell=data.DEFAULT_MIN_VOLUME_SELL,
                                      min_volume_buy=data.DEFAULT_MIN_VOLUME_BUY)
        for ob_item in ob_items:
            assert fields.data_valid(ob_item, fields.ORDER_BOOK_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_trades(self, rest: BitmexRestApi, schema: str):
        lt_items = rest.list_trades(schema=cfg.BITMEX_SCHEMA, symbol=cfg.BITMEX_SYMBOL)
        for lt_item in lt_items:
            assert fields.data_valid(lt_item, fields.TRADE_FIELDS)

    @pytest.mark.parametrize(
        'rest', ['tbitmex'],
        indirect=True
    )
    def test_get_wallet(self, rest: BitmexRestApi):
        wallet = rest.get_wallet()
        assert fields.data_valid(wallet, fields.WALLET_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_wallet_summery(self, rest: BitmexRestApi, schema: str):
        wallet_summary = rest.get_wallet_summary(schemas=[schema])
        assert fields.data_valid(wallet_summary, fields.WALLET_SUMMARY_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_wallet_detail(self, rest: BitmexRestApi, schema: str):
        wallet_detail = rest.get_wallet_detail(schema=schema, asset=data.ASSET)
        assert fields.data_valid(wallet_detail[schema], fields.WALLET_DETAIL_FIELDS[schema])

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_ping(self, rest: BitmexRestApi, schema: str):
        assert rest.ping(schema=schema)

    @pytest.mark.parametrize(
        'rest, schemas', [('tbitmex', [OrderSchema.margin1])],
        indirect=['rest'],
    )
    def test_get_api_key_permission(self, rest: BitmexRestApi, schemas: list):
        permissions = rest.get_api_key_permissions(schemas=schemas)
        for schema in schemas:
            assert permissions[schema]

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_cross_collaterals(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.get_cross_collaterals(schema=schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_assets_balance(self, rest: BitmexRestApi, schema: str):
        assets_balance = rest.get_assets_balance(schema=schema)
        assert fields.data_valid(assets_balance, fields.ASSETS_BALANCE[schema])

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=True,
    )
    def test_wallet_transfer(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_transfer(from_wallet='', to_wallet='', asset=get_asset(schema), amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_wallet_borrow(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_borrow(schema=schema, asset=data.ASSET, amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_wallet_repay(self, rest: BitmexRestApi, schema: str):
        with pytest.raises(ConnectorError):
            rest.wallet_repay(schema=schema, asset=data.ASSET, amount=data.DEFAULT_AMOUNT)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_symbol(self, rest: BitmexRestApi, schema: str):
        symbol = rest.get_symbol(schema=schema, symbol=data.SYMBOL)
        assert fields.data_valid(symbol, fields.SYMBOL_FIELDS)

    # TODO: None in expiration_data
    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_exchange_symbol_info(self, rest: BitmexRestApi, schema: str):
        exchange_symbols = rest.get_exchange_symbol_info(schema=schema)
        for exchange_symbol in exchange_symbols:
            # TODO: TypeError: strptime() argument 1 must be str, not None
            assert fields.data_valid(exchange_symbol, fields.EXCHANGE_SYMBOL_INFO_FIELDS[schema])

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_currency_exchange_symbols(self, rest: BitmexRestApi, schema: str):
        symbols_data = rest.currency_exchange_symbols(schema=schema)
        for symbol_data in symbols_data:
            assert fields.data_valid(symbol_data, fields.CURRENCY_EXCHANGE_SYMBOL_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_symbols_currencies(self, rest: BitmexRestApi, schema: str):
        symbols_currencies = rest.get_symbols_currencies(schema=schema)
        for symbol in symbols_currencies.values():
            assert fields.data_valid(symbol, fields.SYMBOL_CURRENCY_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_order_commissions(self, rest: BitmexRestApi, schema: str):
        orders_commissions = rest.list_order_commissions(schema=schema)
        for commission in orders_commissions:
            assert fields.data_valid(commission, fields.ORDER_COMMISSION_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
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
            ('tbitmex', OrderSchema.margin1, 8, 1)
        ],
        indirect=['rest'],
    )
    def test_get_funding_rates(self, rest: BitmexRestApi,
                                           schema: str, period_hour: int, period_multiplier: int):
        funding_rates = rest.get_funding_rates(schema=schema, symbol=get_symbol(schema), period_hour=period_hour,
                                               period_multiplier=period_multiplier)
        for funding_rate in funding_rates:
            assert fields.data_valid(funding_rate, fields.FUNDING_RATE_FIELDS)
            assert int(funding_rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier', [
            ('tbitmex', OrderSchema.margin1, 8, 1)
        ],
        indirect=['rest'],
    )
    def test_list_funding_rates(self, rest: BitmexRestApi,
                                            schema: str, period_hour: int, period_multiplier: int):
        funding_rates = rest.list_funding_rates(schema=schema, period_hour=period_hour,
                                                period_multiplier=period_multiplier)
        for rate in funding_rates:
            assert fields.data_valid(rate, fields.FUNDING_RATE_FIELDS)
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_leverage(self, rest: BitmexRestApi, schema: str):
        resp = rest.get_leverage(schema=schema, symbol=get_symbol(schema))
        assert isinstance(resp, tuple)
        assert resp[0] in (LeverageType.cross, LeverageType.isolated)
        assert isinstance(resp[1], float)

    @pytest.mark.parametrize(
        'rest, schema, leverage_type, leverage, expect', [
            ('tbitmex', OrderSchema.margin1, LeverageType.isolated, 90, (LeverageType.isolated, 90)),
            ('tbitmex', OrderSchema.margin1, LeverageType.cross, 100, (LeverageType.cross, 100)),
        ],
        indirect=['rest'],
    )
    def test_change_leverage(self, rest: BitmexRestApi, schema: str,
                             leverage_type: str, leverage: Union[float, int], expect: tuple):
        leverage_data = rest.change_leverage(schema=schema, symbol=get_symbol(schema), leverage_type=leverage_type,
                                             leverage=leverage)
        assert leverage_data == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_position(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema, order_type=OrderType.market)
        position = rest.get_position(schema=schema, symbol=order_data.DEFAULT_SYMBOL)
        assert fields.data_valid(position, fields.POSITION_FIELDS)
        # rest.close_all_orders(schema=schema, symbol=order_data.DEFAULT_SYMBOL) # TODO: enable when bitmex fix his EP

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_list_position(self, rest: BitmexRestApi, schema: str):
        create_default_order(rest, schema, order_type=OrderType.market)
        positions = rest.list_positions(schema=schema)
        for position in positions:
            assert fields.data_valid(position, fields.POSITION_FIELDS)
        # rest.close_all_orders(schema=schema, symbol=order_data.DEFAULT_SYMBOL) # TODO: enable when bitmex fix his EP

    @pytest.mark.parametrize(
        'rest, schema', [('tbitmex', OrderSchema.margin1)],
        indirect=['rest'],
    )
    def test_get_position_state(self, rest: BitmexRestApi, schema: str):
        positions_state = rest.get_positions_state(schema=schema)
        assert isinstance(positions_state, dict)

    @pytest.mark.parametrize(
        'rest, schema, side, volume, price, wallet_balance, wallet_detail, funding_rate, taker_fee, leverage_type, '
        'leverage, expect', [
            ('tbitmex', OrderSchema.margin1, BUY, 100.0, 57000.0, 0.0012, data.WALLET_DATA[OrderSchema.margin1],
             0.0001, 0.05, LeverageType.cross, 100, 34060.3729073
             ),
            ('tbitmex', OrderSchema.margin1, BUY, 100.0, 57000.0, 0.0012, data.WALLET_DATA[OrderSchema.margin1],
             0.0001, 0.05, LeverageType.isolated, 100, 56971.57118598),
        ],
        indirect=['rest'],
    )
    def test_get_liquidation(self, rest: BitmexRestApi, schema: str, side: int, volume: float, price: float,
                             wallet_balance: float, wallet_detail: dict, funding_rate: float, taker_fee: float,
                             leverage_type: str, leverage: Union[float, int], expect: float):
        liquidation_data = rest.get_liquidation(schema=schema, symbol=get_symbol(schema), side=side, volume=volume,
                                                price=price, wallet_balance=wallet_balance, wallet_detail=wallet_detail,
                                                taker_fee=taker_fee, leverage_type=leverage_type, leverage=leverage,
                                                funding_rate=funding_rate)
        assert fields.data_valid(liquidation_data, fields.LIQUIDATION_PRICE_FIELDS)
        assert liquidation_data['liquidation_price'] == expect
