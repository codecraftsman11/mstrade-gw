import pytest
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Optional
from mst_gateway.connector.api import schema as fields
from mst_gateway.connector.api.stocks.binance.rest import BinanceRestApi
from mst_gateway.connector.api.types import LeverageType, OrderExec, OrderSchema, OrderType, BUY, SELL
from mst_gateway.exceptions import ConnectorError
from tests import config as cfg
from .data import storage as state_data
from .data import symbol as symbol_data
from .data import order_book as order_book_data
from .data import order as order_data
from .data import position as position_data


def rest_params(param):
    param_map = {
        'tsbinance': (cfg.BINANCE_SPOT_TESTNET_AUTH_KEYS,
                      [OrderSchema.exchange, OrderSchema.margin2, OrderSchema.margin3]),
        'tfbinance': (cfg.BINANCE_FUTURES_TESTNET_AUTH_KEYS,
                      [OrderSchema.futures, OrderSchema.futures_coin]),
    }
    return param_map[param]


@pytest.fixture(params=['tsbinance', 'tfbinance'])
def rest(request) -> BinanceRestApi:
    param = request.param
    auth, available_schemas = rest_params(param)
    with BinanceRestApi(test=True, name='tbinance', auth=auth, throttle_limit=30,
                        state_storage=deepcopy(state_data.STORAGE_DATA)) as api:
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
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_quote_bins(self, rest: BinanceRestApi, schema):
        quote_bins = rest.list_quote_bins(schema=schema, symbol=get_symbol(schema))
        for qb in quote_bins:
            assert fields.data_valid(qb, fields.QUOTE_BIN_FIELDS)
        assert len(quote_bins) == 100

    @pytest.mark.parametrize(
        'rest', ['tsbinance', 'tfbinance'],
        indirect=True,
    )
    def test_get_user(self, rest: BinanceRestApi):
        assert fields.data_valid(rest.get_user(), fields.USER_FIELDS)

    @pytest.mark.parametrize(
        'rest, schemas, expect', [
            ('tsbinance', [OrderSchema.exchange, OrderSchema.margin2, OrderSchema.margin3,
                           OrderSchema.futures, OrderSchema.futures_coin], {
                 OrderSchema.exchange: True,
                 OrderSchema.margin2: False,
                 OrderSchema.margin3: False,
                 OrderSchema.futures: False,
                 OrderSchema.futures_coin: False,
             }),
            ('tfbinance', [OrderSchema.exchange, OrderSchema.margin2, OrderSchema.margin3,
                           OrderSchema.futures, OrderSchema.futures_coin], {
                 OrderSchema.exchange: False,
                 OrderSchema.margin2: False,
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
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_wallet(self, rest: BinanceRestApi, schema):
        wallet = rest.get_wallet(schema=schema)
        assert fields.data_valid(wallet, fields.WALLET_FIELDS[schema])
        for balance in wallet['balances']:
            assert fields.data_valid(balance, fields.BALANCE_FIELDS[schema])
        assert fields.data_valid(wallet['total_balance'], fields.SUMMARY_FIELDS)
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            for key in ('total_unrealised_pnl', 'total_margin_balance', 'total_borrowed', 'total_interest'):
                assert fields.data_valid(wallet[key], fields.SUMMARY_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tsbinance', OrderSchema.exchange, [OrderSchema.exchange]),
            ('tfbinance', OrderSchema.futures, [OrderSchema.exchange, OrderSchema.futures]),
            ('tfbinance', OrderSchema.futures_coin, [OrderSchema.exchange, OrderSchema.futures_coin]),
        ],
        indirect=['rest'],
    )
    def test_get_wallet_detail(self, rest: BinanceRestApi, schema, expect):
        wallet_detail = rest.get_wallet_detail(schema, get_asset(schema))
        assert list(wallet_detail.keys()) == expect
        assert fields.data_valid(wallet_detail[schema], fields.WALLET_DETAIL_FIELDS[schema])

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_wallet_detail_partial(self, rest: BinanceRestApi, schema):
        assert fields.data_valid(rest.get_wallet_detail(schema, get_asset(schema), partial=True),
                                 fields.WALLET_DETAIL_FIELDS[schema])

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def tes_get_cross_collaterals_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.get_cross_collaterals(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_assets_balance(self, rest: BinanceRestApi, schema):
        resp = rest.get_assets_balance(schema)
        assert 'btc' in resp or 'usdt' in resp or 'bnb' in resp

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_symbol(self, rest: BinanceRestApi, schema):
        assert fields.data_valid(rest.get_symbol(schema=schema, symbol=get_symbol(schema)), fields.SYMBOL_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_symbols(self, rest: BinanceRestApi, schema):
        for symbol in rest.list_symbols(schema):
            assert fields.data_valid(symbol, fields.SYMBOL_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_exchange_symbol_info(self, rest: BinanceRestApi, schema):
        for symbol_info in rest.get_exchange_symbol_info(schema):
            assert fields.data_valid(symbol_info, fields.EXCHANGE_SYMBOL_INFO_FIELDS[schema])
            if schema in (OrderSchema.futures, OrderSchema.futures_coin):
                for leverage_bracket in symbol_info['leverage_brackets']:
                    assert fields.data_valid(leverage_bracket, fields.LEVERAGE_BRACKET_FIELDS[schema])

    @classmethod
    def validate_order_book(cls, order_book, side, split, min_volume_buy, min_volume_sell):
        if split:
            for s in order_book:
                for ob in order_book[s]:
                    assert fields.data_valid(ob, fields.ORDER_BOOK_FIELDS)
                    if min_volume_buy and s == BUY:
                        assert ob['volume'] >= min_volume_buy
                    if min_volume_sell and s == SELL:
                        assert ob['volume'] >= min_volume_sell
        else:
            for ob in order_book:
                assert fields.data_valid(ob, fields.ORDER_BOOK_FIELDS)
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
        'rest, schema, count', [('tsbinance', OrderSchema.exchange, None),
                                ('tsbinance', OrderSchema.exchange, 10),
                                ('tsbinance', OrderSchema.exchange, 100),
                                ('tsbinance', OrderSchema.exchange, 1000),
                                ('tsbinance', OrderSchema.margin2, None),
                                ('tsbinance', OrderSchema.margin2, 10),
                                ('tsbinance', OrderSchema.margin2, 100),
                                ('tsbinance', OrderSchema.margin2, 1000),
                                ('tsbinance', OrderSchema.margin3, None),
                                ('tsbinance', OrderSchema.margin3, 10),
                                ('tsbinance', OrderSchema.margin3, 100),
                                ('tsbinance', OrderSchema.margin3, 1000),
                                ('tsbinance', OrderSchema.futures, None),
                                ('tsbinance', OrderSchema.futures, 10),
                                ('tsbinance', OrderSchema.futures, 100),
                                ('tsbinance', OrderSchema.futures, 1000),
                                ('tfbinance', OrderSchema.futures_coin, None),
                                ('tfbinance', OrderSchema.futures_coin, 10),
                                ('tfbinance', OrderSchema.futures_coin, 100),
                                ('tfbinance', OrderSchema.futures_coin, 1000)],
        indirect=['rest'],
    )
    def test_list_trades(self, rest: BinanceRestApi, schema: str, count: Optional[int]):
        trades = rest.list_trades(schema=schema, symbol=get_symbol(schema), count=count)
        for trade in trades:
            assert fields.data_valid(trade, fields.TRADE_FIELDS)
        if count:
            assert len(trades) == count

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_currency_exchange_symbols(self, rest: BinanceRestApi, schema):
        for symbol in rest.currency_exchange_symbols(schema):
            assert fields.data_valid(symbol, fields.CURRENCY_EXCHANGE_SYMBOL_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_symbols_currencies(self, rest: BinanceRestApi, schema):
        for symbol in rest.get_symbols_currencies(schema).values():
            assert fields.data_valid(symbol, fields.SYMBOL_CURRENCY_FIELDS)

    @pytest.mark.parametrize(
        'rest, schemas', [('tsbinance', [OrderSchema.exchange, OrderSchema.margin2, OrderSchema.margin3,
                                         OrderSchema.futures, OrderSchema.futures_coin]),
                          ('tfbinance', [OrderSchema.exchange, OrderSchema.margin2, OrderSchema.margin3,
                                         OrderSchema.futures, OrderSchema.futures_coin])],
        indirect=['rest'],
    )
    def test_get_wallet_summary(self, rest: BinanceRestApi, schemas):
        wallet_summary = rest.get_wallet_summary(schemas)
        assert fields.data_valid(wallet_summary, fields.WALLET_SUMMARY_FIELDS)
        for summary in wallet_summary.values():
            assert fields.data_valid(summary, fields.SUMMARY_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_order_commissions(self, rest: BinanceRestApi, schema):
        for commission in rest.list_order_commissions(schema):
            assert fields.data_valid(commission, fields.ORDER_COMMISSION_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
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
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_alt_currency_commission(self, rest: BinanceRestApi, schema):
        assert fields.data_valid(rest.get_alt_currency_commission(schema), fields.ALT_CURRENCY_COMMISSION_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier, ', [('tsbinance', OrderSchema.exchange, 8, 1),
                                                           ('tsbinance', OrderSchema.margin2, 8, 1),
                                                           ('tfbinance', OrderSchema.futures, 8, 1),
                                                           ('tfbinance', OrderSchema.futures_coin, 8, 1)],
        indirect=['rest'],
    )
    def test_get_funding_rates(self, rest: BinanceRestApi, schema, period_hour, period_multiplier):
        for rate in rest.get_funding_rates(schema=schema, symbol=get_symbol(schema),
                                           period_hour=period_hour, period_multiplier=period_multiplier):
            assert fields.data_valid(rate, fields.FUNDING_RATE_FIELDS)
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema, period_hour, period_multiplier', [('tsbinance', OrderSchema.exchange, 8, 1),
                                                         ('tsbinance', OrderSchema.exchange, 8, 2),
                                                         ('tsbinance', OrderSchema.margin2, 8, 1),
                                                         ('tsbinance', OrderSchema.margin2, 8, 2),
                                                         ('tfbinance', OrderSchema.futures, 8, 1),
                                                         ('tfbinance', OrderSchema.futures, 8, 2)],
        indirect=['rest'],
    )
    def test_list_funding_rates(self, rest: BinanceRestApi, schema, period_hour, period_multiplier):
        for rate in rest.list_funding_rates(schema, period_hour=period_hour, period_multiplier=period_multiplier):
            assert fields.data_valid(rate, fields.FUNDING_RATE_FIELDS)
            assert int(rate.get('time').timestamp() * 1000) > int((datetime.now() - timedelta(
                hours=period_hour * period_multiplier, minutes=1
            )).timestamp() * 1000)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.margin3), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_funding_rates_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.list_funding_rates(schema, period_multiplier=1)

    @pytest.mark.parametrize(
        'rest, schema', [('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_leverage(self, rest: BinanceRestApi, schema):
        resp = rest.get_leverage(schema=schema, symbol=get_symbol(schema))
        assert isinstance(resp, tuple)
        assert resp[0] in (LeverageType.cross, LeverageType.isolated)
        assert isinstance(resp[1], float)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3)],
        indirect=['rest'],
    )
    def test_get_leverage_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.get_leverage(schema=schema, symbol=get_symbol(schema))

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tsbinance', OrderSchema.margin3)],
        indirect=['rest'],
    )
    def test_change_leverage_invalid_schema(self, rest: BinanceRestApi, schema):
        with pytest.raises(ConnectorError):
            rest.change_leverage(schema=schema, symbol=get_symbol(schema),
                                 leverage_type=LeverageType.isolated, leverage=1,
                                 leverage_type_update=True, leverage_update=True)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_position(self, rest: BinanceRestApi, schema):
        position = rest.get_position(schema, get_symbol(schema), account_id=1)
        assert fields.data_valid(position, fields.POSITION_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_positions(self, rest: BinanceRestApi, schema):
        for position in rest.list_positions(schema, account_id=1):
            assert fields.data_valid(position, fields.POSITION_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tsbinance', OrderSchema.margin2),
                         ('tfbinance', OrderSchema.futures), ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_positions_state(self, rest: BinanceRestApi, schema):
        for position_state in rest.get_positions_state(schema).values():
            assert fields.data_valid(position_state, fields.POSITION_STATE_FIELDS)

    @pytest.mark.parametrize(
        'rest, schema, side, volume, mark_price, price, wallet_balance, leverage_type, expect',
        [
            ('tsbinance', OrderSchema.exchange, BUY, 0.1, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             None),
            ('tsbinance', OrderSchema.margin2, BUY, 0.1, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             None),
            ('tfbinance', OrderSchema.futures, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             45733.668341708544),
            ('tfbinance', OrderSchema.futures, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             45733.668341708544),
            ('tfbinance', OrderSchema.futures, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             65278.606965174135),
            ('tfbinance', OrderSchema.futures, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             65278.606965174135),
            ('tfbinance', OrderSchema.futures_coin, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
             0.010040001807218073),
            ('tfbinance', OrderSchema.futures_coin, BUY, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.cross,
             0.010040001807218073),
            ('tfbinance', OrderSchema.futures_coin, SELL, 1.0, 55555.0, 55555.0, 10000.0, LeverageType.isolated,
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
        assert fields.data_valid(liquidation, fields.LIQUIDATION_FIELDS)
        assert liquidation['liquidation_price'] == expect


class TestBinanceRestApiOrder:

    @pytest.mark.parametrize(
        'rest, schema, side, order_type, expect', [
            ('tsbinance', OrderSchema.exchange, BUY, OrderType.market, {
                 'active': True,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tsbinance', OrderSchema.exchange, SELL, OrderType.market, {
                 'active': True,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': 'SELL',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tsbinance', OrderSchema.exchange, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tsbinance', OrderSchema.exchange, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.exchange,
                 'side': 'SELL',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
             }),
            ('tfbinance', OrderSchema.futures, BUY, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tfbinance', OrderSchema.futures, SELL, OrderType.market,  {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': 'SELL',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tfbinance', OrderSchema.futures, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tfbinance', OrderSchema.futures, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures,
                 'side': 'SELL',
                 'stop': 0.0,
                 'symbol': 'BTCUSDT',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
             }),
            ('tfbinance', OrderSchema.futures_coin, BUY, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tfbinance', OrderSchema.futures_coin, SELL, OrderType.market, {
                 'active': False,
                 'execution': OrderExec.market,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': 'SELL',
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.market,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tfbinance', OrderSchema.futures_coin, BUY, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': 'BUY',
                 'stop': 0.0,
                 'symbol': 'BTCUSD_PERP',
                 'system_symbol': 'btcusd',
                 'type': OrderType.limit,
                 'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures_coin],
             }),
            ('tfbinance', OrderSchema.futures_coin, SELL, OrderType.limit, {
                 'active': False,
                 'execution': OrderExec.limit,
                 'filled_volume': 0.0,
                 'schema': OrderSchema.futures_coin,
                 'side': 'SELL',
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
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        if order_type == OrderType.market:
            order.pop('price')
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_get_order(self, rest: BinanceRestApi, schema):
        default_order = create_default_order(rest, schema)
        expect = deepcopy(order_data.DEFAULT_ORDER[schema])
        expect['price'] = default_order['price']
        order = rest.get_order(default_order['exchange_order_id'], default_order['symbol'], schema)
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_list_orders(self, rest: BinanceRestApi, schema):
        default_order = create_default_order(rest, schema)
        orders = rest.list_orders(schema, default_order['symbol'])
        for order in orders:
            assert fields.data_valid(order, fields.ORDER_FIELDS)
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tsbinance', OrderSchema.exchange, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.exchange,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE_STR,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange] * 2,
            }),
            ('tfbinance', OrderSchema.futures, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE_STR,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures] * 2,
            }),
            ('tfbinance', OrderSchema.futures_coin, {
                'active': False,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures_coin,
                'side': order_data.DEFAULT_ORDER_OPPOSITE_SIDE_STR,
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
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        order.pop('price')
        assert order == expect
        rest.cancel_all_orders(schema)

    @pytest.mark.parametrize(
        'rest, schema, expect', [
            ('tsbinance', OrderSchema.exchange, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.exchange,
                'side': order_data.DEFAULT_ORDER_SIDE_STR,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.exchange],
            }),
            ('tfbinance', OrderSchema.futures, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures,
                'side': order_data.DEFAULT_ORDER_SIDE_STR,
                'stop': 0.0,
                'symbol': 'BTCUSDT',
                'system_symbol': 'btcusd',
                'type': OrderType.limit,
                'volume': order_data.DEFAULT_ORDER_VOLUME[OrderSchema.futures],
            }),
            ('tfbinance', OrderSchema.futures_coin, {
                'active': True,
                'execution': OrderExec.limit,
                'filled_volume': 0.0,
                'schema': OrderSchema.futures_coin,
                'side': order_data.DEFAULT_ORDER_SIDE_STR,
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
        assert fields.data_valid(order, fields.ORDER_FIELDS)
        clear_stock_order_data(order)
        assert order == expect

    @pytest.mark.parametrize(
        'rest, schema', [('tsbinance', OrderSchema.exchange), ('tfbinance', OrderSchema.futures),
                         ('tfbinance', OrderSchema.futures_coin)],
        indirect=['rest'],
    )
    def test_cancel_all_orders(self, rest: BinanceRestApi, schema):
        create_default_order(rest, schema)
        assert rest.cancel_all_orders(schema)
