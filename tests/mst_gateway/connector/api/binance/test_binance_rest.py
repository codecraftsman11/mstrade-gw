import logging
import pytest
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from schema import Schema
from mst_gateway.logging import init_logger
from mst_gateway.connector.api.stocks.binance.rest import BinanceRestApi
from mst_gateway.connector.api.types import LeverageType, OrderExec, OrderSchema, OrderType, BUY, SELL
from mst_gateway.exceptions import ConnectorError
from tests.mst_gateway.connector import schema as fields
from tests import config as cfg
from .data import storage as state_data
from .data import symbol as symbol_data
from .data import order_book as order_book_data
from .data import order as order_data
from .data import position as position_data


def rest_params(param):
    param_map = {
        'tbinance_spot': (cfg.BINANCE_SPOT_TESTNET_AUTH_KEYS,
                          [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin3]),
        'tbinance_futures': (cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS,
                             [OrderSchema.futures, OrderSchema.futures_coin]),
    }
    return param_map[param]


@pytest.fixture
def _debug(caplog):
    logger = init_logger(name="test", level=logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="test")
    yield {'logger': logger, 'caplog': caplog}


@pytest.fixture(params=['tbinance_spot', 'tbinance_futures'])
def rest(request, _debug) -> BinanceRestApi:
    param = request.param
    auth, available_schemas = rest_params(param)
    with BinanceRestApi(test=True, name='tbinance', auth=auth, throttle_limit=30,
                        state_storage=deepcopy(state_data.STORAGE_DATA),
                        logger=_debug['logger']) as api:
        api.open()
        for schema in available_schemas:
            assert api.ping(schema)
        yield api
        api.close()


def get_asset(schema):
    return 'BTC' if schema == OrderSchema.futures_coin else 'USDT'


def get_symbol(schema):
    return 'BTCUSD_PERP' if schema == OrderSchema.futures_coin else 'BTCUSDT'


def get_order_price(rest: BinanceRestApi, schema, symbol, side) -> float:
    symbol = rest.get_symbol(symbol, schema)
    if side == BUY:
        return round(symbol.get('bid_price') / 1.1, 1)
    return round(symbol.get('ask_price') * 1.1, 1)


def create_default_order(rest: BinanceRestApi, schema):
    symbol = get_symbol(schema)
    return rest.create_order(
        schema=schema,
        symbol=symbol,
        side=order_data.DEFAULT_ORDER_SIDE,
        volume=order_data.DEFAULT_ORDER_VOLUME[schema],
        order_type=OrderType.limit,
        price=get_order_price(rest, schema, symbol, order_data.DEFAULT_ORDER_SIDE),
        options=order_data.DEFAULT_ORDER_OPTIONS,
    )


def clear_stock_order_data(order):
    order.pop('time')
    order.pop('exchange_order_id')


def get_liquidation_kwargs(schema):
    return symbol_data.DEFAULT_LEVERAGE_BRACKETS.get(schema, []), \
           position_data.DEFAULT_POSITIONS_STATE.get(schema, {})


class TestBinanceRestApi:

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_quote_bins(self, rest: BinanceRestApi, schema):
        quote_bins = rest.list_quote_bins(schema=schema, symbol=get_symbol(schema))
        quote_bin_schema = Schema(fields.QUOTE_BIN_FIELDS)
        for qb in quote_bins:
            assert quote_bin_schema.validate(qb) == qb
        assert len(quote_bins) == 100

    @pytest.mark.parametrize(
        'rest', ['tbinance_spot', 'tbinance_futures'],
        indirect=True,
    )
    def test_get_user(self, rest: BinanceRestApi):
        user = rest.get_user()
        user_schema = Schema(fields.USER_FIELDS)
        assert user_schema.validate(user) == user

    @pytest.mark.parametrize(
        'rest, schemas, expect', [
            ('tbinance_spot', [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin3,
                               OrderSchema.futures, OrderSchema.futures_coin], {
                 OrderSchema.exchange: True,
                 OrderSchema.margin_cross: False,
                 OrderSchema.margin3: False,
                 OrderSchema.futures: False,
                 OrderSchema.futures_coin: False,
             }),
            ('tbinance_futures', [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin3,
                                  OrderSchema.futures, OrderSchema.futures_coin], {
                 OrderSchema.exchange: False,
                 OrderSchema.margin_cross: False,
                 OrderSchema.margin3: False,
                 OrderSchema.futures: True,
                 OrderSchema.futures_coin: True,
             }),
        ],
        indirect=['rest'],
    )
    def test_get_api_key_permissions(self, rest: BinanceRestApi, schemas, expect):
        assert rest.get_api_key_permissions(schemas) == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_wallet(self, rest: BinanceRestApi, schema):
        wallet = rest.get_wallet(schema=schema)
        assert Schema(fields.WALLET_FIELDS).validate(wallet) == wallet
        balance_schema = Schema(fields.WALLET_BALANCE_FIELDS)
        for balance in wallet['balances']:
            assert balance_schema.validate(balance) == balance

        total_cross_schema = Schema(fields.TOTAL_CROSS_AMOUNT_FIELDS)
        for key in wallet.keys():
            if key.startswith('total_'):
                assert total_cross_schema.validate(wallet[key]) == wallet[key]

        if extra_data := wallet['extra_data']:
            assert Schema(fields.WALLET_EXTRA_FIELDS[schema]).validate(extra_data) == extra_data
            if extra_data.get('balances'):
                extra_balance_schema = Schema(fields.WALLET_EXTRA_BALANCE_FIELDS[schema])
                for extra_balance in extra_data['balances']:
                    assert extra_balance_schema.validate(extra_balance) == extra_balance

                for key in extra_data.keys():
                    if key.startswith('total_'):
                        assert total_cross_schema.validate(extra_data[key]) == extra_data[key]

    @pytest.mark.parametrize(
        'rest, schema', [
            ('tbinance_spot', OrderSchema.exchange),
            ('tbinance_futures', OrderSchema.futures),
            ('tbinance_futures', OrderSchema.futures_coin),
        ],
        indirect=['rest'],
    )
    def test_get_wallet_detail(self, rest: BinanceRestApi, schema):
        wallet_detail = rest.get_wallet_detail(schema=schema, asset=get_asset(schema))
        assert Schema(fields.WALLET_BALANCE_FIELDS).validate(wallet_detail) == wallet_detail

    @pytest.mark.parametrize(
        'rest, schema', [
            ('tbinance_spot', OrderSchema.exchange),
            ('tbinance_futures', OrderSchema.futures),
            ('tbinance_futures', OrderSchema.futures_coin),
        ],
        indirect=['rest'],
    )
    def test_get_wallet_extra_data(self, rest: BinanceRestApi, schema):
        wallet_extra = rest.get_wallet_extra_data(schema=schema, asset=get_asset(schema))
        if wallet_extra:
            assert Schema(fields.WALLET_EXTRA_DATA_FIELDS[schema]).validate(wallet_extra) == wallet_extra

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_assets_balance(self, rest: BinanceRestApi, schema):
        assets_balance = rest.get_assets_balance(schema)
        asset_balance_schema = Schema(fields.ASSETS_BALANCE)
        for a, b in assets_balance.items():
            assert asset_balance_schema.validate({a: b}) == {a: b}

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_symbol(self, rest: BinanceRestApi, schema):
        symbol = rest.get_symbol(schema=schema, symbol=get_symbol(schema))
        assert Schema(fields.SYMBOL_FIELDS).validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_symbols(self, rest: BinanceRestApi, schema):
        symbol_schema = Schema(fields.SYMBOL_FIELDS)
        for symbol in rest.list_symbols(schema):
            assert symbol_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_exchange_symbol_info(self, rest: BinanceRestApi, schema):
        symbol_info_schema = Schema(fields.EXCHANGE_SYMBOL_INFO_FIELDS[schema])
        for symbol_info in rest.get_exchange_symbol_info(schema):
            assert symbol_info_schema.validate(symbol_info) == symbol_info
            if schema in (OrderSchema.futures, OrderSchema.futures_coin):
                leverage_bracket_schema = Schema(fields.LEVERAGE_BRACKET_FIELDS[schema])
                for leverage_bracket in symbol_info['leverage_brackets']:
                    assert leverage_bracket_schema.validate(leverage_bracket) == leverage_bracket

    @classmethod
    def validate_order_book(cls, order_book, side, split, min_volume_buy, min_volume_sell):
        order_book_schema = Schema(fields.ORDER_BOOK_FIELDS)
        if split:
            for s in order_book:
                for ob in order_book[s]:
                    assert order_book_schema.validate(ob) == ob
                    if min_volume_buy and s == BUY:
                        assert ob['volume'] >= min_volume_buy
                    if min_volume_sell and s == SELL:
                        assert ob['volume'] >= min_volume_sell
        else:
            for ob in order_book:
                assert order_book_schema.validate(ob) == ob
                if side is not None:
                    assert ob['side'] == side
                if min_volume_buy is not None and ob['side'] == BUY:
                    assert ob['volume'] >= min_volume_buy
                if min_volume_sell is not None and ob['side'] == SELL:
                    assert ob['volume'] >= min_volume_sell

    @pytest.mark.parametrize(
        'rest, schema, side, split, min_volume_buy, min_volume_sell', order_book_data.ORDER_BOOK_PARAMS,
        indirect=['rest'],
    )
    def test_get_order_book(self, rest: BinanceRestApi, schema, side, split, min_volume_buy, min_volume_sell):
        order_book = rest.get_order_book(schema=schema, symbol=get_symbol(schema), side=side, split=split,
                                         min_volume_buy=min_volume_buy, min_volume_sell=min_volume_sell)
        self.validate_order_book(order_book, side, split, min_volume_buy, min_volume_sell)

    @pytest.mark.parametrize(
        'rest, schema, side, split, min_volume_buy, min_volume_sell', order_book_data.ORDER_BOOK_PARAMS,
        indirect=['rest'],
    )
    def test_list_order_book(self, rest: BinanceRestApi, schema, side, split, min_volume_buy, min_volume_sell):
        order_book = rest.list_order_book(schema=schema, symbol=get_symbol(schema), side=side, split=split,
                                          min_volume_buy=min_volume_buy, min_volume_sell=min_volume_sell)
        self.validate_order_book(order_book, side, split, min_volume_buy, min_volume_sell)

    @pytest.mark.parametrize(
        'rest, schema, count', [('tbinance_spot', OrderSchema.exchange, None),
                                ('tbinance_spot', OrderSchema.exchange, 10),
                                ('tbinance_spot', OrderSchema.exchange, 100),
                                ('tbinance_spot', OrderSchema.exchange, 1000),
                                ('tbinance_spot', OrderSchema.margin_cross, None),
                                ('tbinance_spot', OrderSchema.margin_cross, 10),
                                ('tbinance_spot', OrderSchema.margin_cross, 100),
                                ('tbinance_spot', OrderSchema.margin_cross, 1000),
                                ('tbinance_spot', OrderSchema.margin3, None),
                                ('tbinance_spot', OrderSchema.margin3, 10),
                                ('tbinance_spot', OrderSchema.margin3, 100),
                                ('tbinance_spot', OrderSchema.margin3, 1000),
                                ('tbinance_spot', OrderSchema.futures, None),
                                ('tbinance_spot', OrderSchema.futures, 10),
                                ('tbinance_spot', OrderSchema.futures, 100),
                                ('tbinance_spot', OrderSchema.futures, 1000),
                                ('tbinance_futures', OrderSchema.futures_coin, None),
                                ('tbinance_futures', OrderSchema.futures_coin, 10),
                                ('tbinance_futures', OrderSchema.futures_coin, 100),
                                ('tbinance_futures', OrderSchema.futures_coin, 1000)],
        indirect=['rest'],
    )
    def test_list_trades(self, rest: BinanceRestApi, schema: str, count: Optional[int]):
        trades = rest.list_trades(schema=schema, symbol=get_symbol(schema), count=count)
        trade_schema = Schema(fields.TRADE_FIELDS)
        for trade in trades:
            assert trade_schema.validate(trade) == trade
        if count:
            assert len(trades) == count

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_currency_exchange_symbols(self, rest: BinanceRestApi, schema):
        symbol_schema = Schema(fields.CURRENCY_EXCHANGE_SYMBOL_FIELDS)
        for symbol in rest.currency_exchange_symbols(schema):
            assert symbol_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_symbols_currencies(self, rest: BinanceRestApi, schema):
        symbol_schema = Schema(fields.SYMBOL_CURRENCY_FIELDS)
        for symbol in rest.get_symbols_currencies(schema).values():
            assert symbol_schema.validate(symbol) == symbol

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange),
                         ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_wallet_summary(self, rest: BinanceRestApi, schema):
        wallet_summary = rest.get_wallet_summary(schema)
        assert Schema(fields.WALLET_SUMMARY_FIELDS).validate(wallet_summary) == wallet_summary

        total_cross_schema = Schema(fields.TOTAL_CROSS_AMOUNT_FIELDS)
        for key in wallet_summary.keys():
            assert total_cross_schema.validate(wallet_summary[key]) == wallet_summary[key]

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_order_commissions(self, rest: BinanceRestApi, schema):
        commission_schema = Schema(fields.ORDER_COMMISSION_FIELDS)
        for commission in rest.list_order_commissions(schema):
            assert commission_schema.validate(commission) == commission

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_vip_level(self, rest: BinanceRestApi, schema):
        level = rest.get_vip_level(schema)
        assert isinstance(level, str)
        try:
            int_level = int(level)
        except (TypeError, ValueError):
            int_level = None
        assert isinstance(int_level, int)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_alt_currency_commission(self, rest: BinanceRestApi, schema):
        commission = rest.get_alt_currency_commission(schema)
        assert Schema(fields.ALT_CURRENCY_COMMISSION_FIELDS).validate(commission) == commission

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier, ', [('tbinance_spot', OrderSchema.exchange, 8, 1),
                                                           ('tbinance_spot', OrderSchema.margin_cross, 8, 1),
                                                           ('tbinance_futures', OrderSchema.futures, 8, 1),
                                                           ('tbinance_futures', OrderSchema.futures_coin, 8, 1)],
        indirect=['rest'],
    )
    def test_get_funding_rates(self, rest: BinanceRestApi, schema, period_hour, period_multiplier):
        rate_schema = Schema(fields.FUNDING_RATE_FIELDS)
        for rate in rest.get_funding_rates(schema=schema, symbol=get_symbol(schema),
                                           period_hour=period_hour, period_multiplier=period_multiplier):
            assert rate_schema.validate(rate) == rate
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier', [('tbinance_spot', OrderSchema.exchange, 8, 1),
                                                         ('tbinance_spot', OrderSchema.exchange, 8, 2),
                                                         ('tbinance_spot', OrderSchema.margin_cross, 8, 1),
                                                         ('tbinance_spot', OrderSchema.margin_cross, 8, 2),
                                                         ('tbinance_futures', OrderSchema.futures, 8, 1),
                                                         ('tbinance_futures', OrderSchema.futures, 8, 2)],
        indirect=['rest'],
    )
    def test_list_funding_rates(self, rest: BinanceRestApi, schema, period_hour, period_multiplier):
        rate_schema = Schema(fields.FUNDING_RATE_FIELDS)
        for rate in rest.list_funding_rates(schema, period_hour=period_hour, period_multiplier=period_multiplier):
            assert rate_schema.validate(rate) == rate
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.margin3), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_funding_rates_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.list_funding_rates(schema, period_multiplier=1)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_leverage(self, rest: BinanceRestApi, schema):
        resp = rest.get_leverage(schema=schema, symbol=get_symbol(schema))
        assert isinstance(resp, tuple)
        assert resp[0] in (LeverageType.cross, LeverageType.isolated)
        assert isinstance(resp[1], float)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3)],
        indirect=['rest'],
    )
    def test_get_leverage_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.get_leverage(schema=schema, symbol=get_symbol(schema))

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_spot', OrderSchema.margin3)],
        indirect=['rest'],
    )
    def test_change_leverage_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.change_leverage(schema=schema, symbol=get_symbol(schema),
                                 leverage_type=LeverageType.isolated, leverage=1,
                                 leverage_type_update=True, leverage_update=True)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_position(self, rest: BinanceRestApi, schema):
        position = rest.get_position(schema, get_symbol(schema), account_id=1)
        assert Schema(fields.POSITION_FIELDS).validate(position) == position

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_positions(self, rest: BinanceRestApi, schema):
        position_schema = Schema(fields.POSITION_FIELDS)
        for position in rest.list_positions(schema, account_id=1):
            assert position_schema.validate(position) == position

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_spot', OrderSchema.margin_cross),
                         ('tbinance_futures', OrderSchema.futures), ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_positions_state(self, rest: BinanceRestApi, schema):
        position_state_schema = Schema(fields.POSITION_STATE_FIELDS)
        for position_state in rest.get_positions_state(schema).values():
            assert position_state_schema.validate(position_state) == position_state

    @pytest.mark.parametrize(
        'rest, schema, side, volume, mark_price, price, wallet_balance, leverage_type, expect',
        [
            ('tbinance_spot', OrderSchema.exchange, BUY, 0.1, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             None),
            ('tbinance_spot', OrderSchema.margin_cross, BUY, 0.1, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             None),
            ('tbinance_futures', OrderSchema.futures, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             45733.668341708544),
            ('tbinance_futures', OrderSchema.futures, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             45733.668341708544),
            ('tbinance_futures', OrderSchema.futures, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             65278.606965174135),
            ('tbinance_futures', OrderSchema.futures, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             65278.606965174135),
            ('tbinance_futures', OrderSchema.futures_coin, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             0.010040001807218073),
            ('tbinance_futures', OrderSchema.futures_coin, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             0.010040001807218073),
            ('tbinance_futures', OrderSchema.futures_coin, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             None),
        ],
        indirect=['rest'],
    )
    def test_get_liquidation(self, rest: BinanceRestApi, schema: str, side: int, volume: float, mark_price: float,
                             price: float, wallet_balance: float, leverage_type: str, expect: Optional[float]):
        leverage_brackets, positions_state = get_liquidation_kwargs(schema)
        liquidation = rest.get_liquidation(get_symbol(schema), schema,
                                           leverage_type, wallet_balance, side, volume, price, mark_price=mark_price,
                                           leverage_brackets=leverage_brackets, positions_state=positions_state)
        assert Schema(fields.LIQUIDATION_FIELDS).validate(liquidation) == liquidation
        assert liquidation['liquidation_price'] == expect


class TestOrderBinanceRestApi:

    @pytest.mark.parametrize(
        'rest, schema, side, order_type, expect', [
            ('tbinance_spot', OrderSchema.exchange, BUY, OrderType.market, {
                 'active': True,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tbinance_spot', OrderSchema.exchange, SELL, OrderType.market, {
                 'active': True,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tbinance_spot', OrderSchema.exchange, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tbinance_spot', OrderSchema.exchange, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tbinance_futures', OrderSchema.futures, BUY, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tbinance_futures', OrderSchema.futures, SELL, OrderType.market,  {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tbinance_futures', OrderSchema.futures, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tbinance_futures', OrderSchema.futures, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tbinance_futures', OrderSchema.futures_coin, BUY, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tbinance_futures', OrderSchema.futures_coin, SELL, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tbinance_futures', OrderSchema.futures_coin, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': BUY,
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tbinance_futures', OrderSchema.futures_coin, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': SELL,
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
        ],
        indirect=['rest'],
    )
    def test_create_order(self, rest: BinanceRestApi, schema, side, order_type, expect):
        symbol = get_symbol(schema)
        price = None
        if order_type == OrderType.limit:
            price = get_order_price(rest, schema, symbol, side)
            expect['price'] = price
        order = rest.create_order(symbol, schema, side, order_data.DEFAULT_ORDER_VOLUME[schema], order_type, price,
                                  order_data.DEFAULT_ORDER_OPTIONS)
        assert Schema(fields.ORDER_FIELDS).validate(order) == order
        clear_stock_order_data(order)
        if order_type == OrderType.market:
            order.pop('price')
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_order(self, rest: BinanceRestApi, schema):
        default_order = create_default_order(rest, schema)
        expect = deepcopy(order_data.DEFAULT_ORDER[schema])
        expect['price'] = default_order['price']
        order = rest.get_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert Schema(fields.ORDER_FIELDS).validate(order) == order
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_orders(self, rest: BinanceRestApi, schema):
        default_order = create_default_order(rest, schema)
        orders = rest.list_orders(schema, default_order['symbol'])
        order_schema = Schema(fields.ORDER_FIELDS)
        for order in orders:
            assert order_schema.validate(order) == order
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tbinance_spot', OrderSchema.exchange, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.exchange,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange] * 2,
            }),
            ('tbinance_futures', OrderSchema.futures, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures] * 2,
            }),
            ('tbinance_futures', OrderSchema.futures_coin, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures_coin,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSD_PERP',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin] * 2,
            }),
        ],
        indirect=['rest'],
    )
    def test_update_order(self, rest: BinanceRestApi, schema: str, expect):
        default_order = create_default_order(rest, schema)
        symbol = get_symbol(schema)
        order = rest.update_order(default_order['exchange_order_id'], symbol, schema,
                                  side=order_data.DEFAULT_ORDER_OPPOSITE_SIDE,
                                  volume=default_order['volume'] * 2,
                                  order_type=OrderType.limit,
                                  price=get_order_price(rest, schema, symbol, order_data.DEFAULT_ORDER_OPPOSITE_SIDE),
                                  options=order_data.DEFAULT_ORDER_OPTIONS)
        assert Schema(fields.ORDER_FIELDS).validate(order) == order
        clear_stock_order_data(order)
        order.pop('price')
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tbinance_spot', OrderSchema.exchange, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.exchange,
                'side': order_data.DEFAULT_ORDER_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
            }),
            ('tbinance_futures', OrderSchema.futures, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures,
                'side': order_data.DEFAULT_ORDER_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
            }),
            ('tbinance_futures', OrderSchema.futures_coin, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures_coin,
                'side': order_data.DEFAULT_ORDER_SIDE,
                'stop': 0.0,
                'symbol': 'BTCUSD_PERP',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
            }),
        ],
        indirect=['rest'],
    )
    def test_cancel_order(self, rest: BinanceRestApi, schema: str, expect: dict):
        default_order = create_default_order(rest, schema)
        expect['price'] = default_order['price']
        order = rest.cancel_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert Schema(fields.ORDER_FIELDS).validate(order) == order
        clear_stock_order_data(order)
        assert order == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tbinance_spot', OrderSchema.exchange), ('tbinance_futures', OrderSchema.futures),
                         ('tbinance_futures', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_cancel_all_orders(self, rest: BinanceRestApi, schema):
        create_default_order(rest, schema)
        assert rest.cancel_all_orders(schema)
