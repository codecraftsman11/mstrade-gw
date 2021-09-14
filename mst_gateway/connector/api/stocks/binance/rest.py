from uuid import uuid4
from datetime import datetime, timedelta
from typing import Union
from bravado.exception import HTTPError
from binance.exceptions import BinanceAPIException, BinanceRequestException
from mst_gateway.calculator import BinanceFinFactory
from mst_gateway.connector.api.types import OrderSchema, OrderType
from mst_gateway.connector.api.utils.rest import validate_exchange_order_id, validate_schema
from mst_gateway.connector.api.stocks.binance.wss.serializers.position import BinanceFuturesPositionSerializer
from .lib import Client
from . import utils, var
from ...rest import StockRestApi
from ...utils import load_wallet_summary_in_usd, convert_to_currency
from .....exceptions import GatewayError, ConnectorError, RecoverableError, NotFoundError


class BinanceRestApi(StockRestApi):
    name = 'binance'
    fin_factory = BinanceFinFactory()

    def _connect(self, **kwargs):
        return Client(api_key=self._auth.get('api_key'),
                      api_secret=self._auth.get('api_secret'),
                      testnet=self.test)

    def ping(self, schema: str) -> bool:
        schema_handlers = {
            OrderSchema.exchange: self._handler.spot_ping,
            OrderSchema.margin2: self._handler.margin_ping,
            OrderSchema.futures: self._handler.futures_ping,
            OrderSchema.futures_coin: self._handler.futures_coin_ping,
        }
        try:
            self._binance_api(schema_handlers[schema.lower()])
        except (KeyError, GatewayError):
            return False
        return True

    def get_user(self) -> dict:
        try:
            data = self._binance_api(self._handler.get_deposit_address, coin='eth')
        except ConnectorError as e:
            if not self.name.startswith('t'):
                raise ConnectorError(e)
            data = {'address': uuid4()}
        return utils.load_user_data(data)

    def get_symbol(self, symbol, schema) -> dict:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_ticker,),
            OrderSchema.margin2: (self._handler.get_ticker,),
            OrderSchema.futures: (
                self._handler.futures_ticker,
                self._handler.futures_orderbook_ticker,
                self._handler.futures_position_information,
            ),
            OrderSchema.futures_coin: (
                self._handler.futures_coin_ticker,
                self._handler.futures_coin_orderbook_ticker,
                self._handler.futures_coin_position_information,
            ),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        symbol = symbol.upper()
        data = self._binance_api(schema_handlers[schema][0], symbol=symbol)
        state_data = self.storage.get('symbol', self.name, schema).get(utils.stock2symbol(symbol), {})
        if schema in (OrderSchema.margin2, OrderSchema.exchange):
            return utils.load_symbol_data(schema, data, state_data)
        if isinstance(data, list):
            data = data[0]
        data_bid_ask_price = self._binance_api(schema_handlers[schema][1], symbol=symbol)
        if isinstance(data_bid_ask_price, list):
            data_bid_ask_price = data_bid_ask_price[0]
        mark_price = None
        for p in self._binance_api(schema_handlers[schema][2]):
            if p['symbol'].upper() == symbol and p.get('positionSide', '').upper() == var.BinancePositionSideMode.BOTH:
                mark_price = p.get('markPrice')
        data.update({
            'bidPrice': data_bid_ask_price.get('bidPrice'),
            'askPrice': data_bid_ask_price.get('askPrice'),
            'markPrice': mark_price,
        })
        return utils.load_futures_symbol_data(schema, data, state_data)

    @staticmethod
    def _update_ticker_data(ticker_data: list, bid_ask_prices: dict, mark_prices: dict) -> list:
        for ticker in ticker_data:
            symbol = ticker['symbol'].lower()
            bid_ask_price = bid_ask_prices.get(symbol, {})
            ticker.update({
                'bidPrice': bid_ask_price.get('bidPrice'),
                'askPrice': bid_ask_price.get('askPrice'),
                'markPrice': mark_prices.get(symbol)
            })
        return ticker_data

    def list_symbols(self, schema, **kwargs) -> list:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_ticker,),
            OrderSchema.margin2: (self._handler.get_ticker,),
            OrderSchema.futures: (
                self._handler.futures_ticker,
                self._handler.futures_orderbook_ticker,
                self._handler.futures_position_information,
            ),
            OrderSchema.futures_coin: (
                self._handler.futures_coin_ticker,
                self._handler.futures_coin_orderbook_ticker,
                self._handler.futures_coin_position_information,
            ),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        data = self._binance_api(schema_handlers[schema][0])
        state_data = self.storage.get('symbol', self.name, schema)
        if schema in (OrderSchema.margin2, OrderSchema.exchange):
            symbols = []
            for d in data:
                symbol_state = state_data.get(d['symbol'].lower())
                if symbol_state and utils.to_float(d.get('weightedAvgPrice')):
                    symbols.append(utils.load_symbol_data(schema, d, symbol_state))
            return symbols
        bid_ask_prices = {bap['symbol'].lower(): bap for bap in self._binance_api(schema_handlers[schema][1])}
        mark_prices = {p['symbol'].lower(): p.get('markPrice') for p in self._binance_api(schema_handlers[schema][2])
                       if p.get('positionSide', '').upper() == var.BinancePositionSideMode.BOTH}
        data = self._update_ticker_data(data, bid_ask_prices, mark_prices)
        return [utils.load_futures_symbol_data(schema, d, state_data[d['symbol'].lower()])
                for d in data if state_data.get(d['symbol'].lower())]

    def get_exchange_symbol_info(self, schema: str) -> list:
        if schema.lower() in (OrderSchema.exchange, OrderSchema.margin2):
            data = self._binance_api(self._handler.get_exchange_info)
            return utils.load_exchange_symbol_info(data.get('symbols', []))
        if schema.lower() in (OrderSchema.futures, OrderSchema.futures_coin):
            schema_handlers = {
                OrderSchema.futures: (
                    self._handler.futures_exchange_info,
                    self._handler.futures_leverage_bracket,
                    utils.load_futures_exchange_symbol_info,
                ),
                OrderSchema.futures_coin: (
                    self._handler.futures_coin_exchange_info,
                    self._handler.futures_coin_leverage_bracket,
                    utils.load_futures_coin_exchange_symbol_info,
                ),
            }
            data = self._binance_api(schema_handlers[schema.lower()][0])
            leverage_data = self._binance_api(schema_handlers[schema.lower()][1])
            return schema_handlers[schema.lower()][2](
                data.get('symbols', []), utils.load_leverage_brackets_as_dict(leverage_data)
            )
        raise ConnectorError(f"Invalid schema {schema}.")

    def _list_quote_bins_page(self, symbol: str, schema: str, binsize: str = '1m', count: int = 100, **kwargs):
        state_data = kwargs.pop('state_data', {})
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_klines,
            OrderSchema.margin2: self._handler.get_klines,
            OrderSchema.futures: self._handler.futures_klines,
            OrderSchema.futures_coin: self._handler.futures_coin_klines,
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(
            schema_handlers[schema.lower()],
            symbol=symbol.upper(),
            interval=binsize,
            limit=count,
            **kwargs,
        )
        return [utils.load_quote_bin_data(d, state_data) for d in data]

    def list_quote_bins(self, symbol, schema, binsize='1m', count=100, **kwargs) -> list:
        pages = int((count - 1) / var.BINANCE_MAX_QUOTE_BINS_COUNT + 1)
        rest = count % var.BINANCE_MAX_QUOTE_BINS_COUNT or var.BINANCE_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        kwargs = self._api_kwargs(kwargs)
        kwargs['state_data'] = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        for i in range(pages):
            if i == pages - 1:
                items_count = rest
            else:
                items_count = var.BINANCE_MAX_QUOTE_BINS_COUNT
            quotes = self._list_quote_bins_page(symbol=symbol,
                                                schema=schema,
                                                binsize=binsize,
                                                count=items_count,
                                                **kwargs)
            if not quotes:
                continue
            if 'startTime' in kwargs:
                kwargs['startTime'] = int(quotes[-1].get('timestamp') + 1)
                quote_bins.extend(quotes)
            else:
                kwargs['endTime'] = int(quotes[0].get('timestamp') - 1)
                quotes.extend(quote_bins)
                quote_bins = quotes
        return quote_bins

    def create_order(self, symbol: str, schema: str, side: int, volume: float,
                     order_type: str = OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        schema_handlers = {
            OrderSchema.exchange: self._handler.create_order,
            OrderSchema.margin2: self._handler.create_margin_order,
            OrderSchema.futures: self._handler.futures_create_order,
            OrderSchema.futures_coin: self._handler.futures_coin_create_order,
        }
        validate_schema(schema, schema_handlers)
        main_params = {
            'symbol': utils.symbol2stock(symbol),
            'order_type': order_type,
            'side': utils.store_order_side(side),
            'volume': volume,
            'price': str(price),
        }
        params = utils.generate_parameters_by_order_type(main_params, options, schema)
        data = self._binance_api(schema_handlers[schema.lower()], **params)
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        return utils.load_order_data(data, state_data)

    def update_order(self, exchange_order_id: str, symbol: str,
                     schema: str, side: int, volume: float,
                     order_type: str = OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        """
        Updates an order by deleting an existing order and creating a new one.

        """
        self.cancel_order(exchange_order_id, symbol, schema)
        return self.create_order(symbol, schema, side, volume, order_type, price, options=options)

    def cancel_all_orders(self, schema: str):
        data = [self.cancel_order(
            exchange_order_id=order["exchange_order_id"],
            symbol=order["symbol"],
            schema=schema
        ) for order in self.list_orders(schema=schema)]
        return bool(data)

    def cancel_order(self, exchange_order_id: str, symbol: str, schema: str) -> dict:
        validate_exchange_order_id(exchange_order_id)
        schema_handlers = {
            OrderSchema.exchange: self._handler.cancel_order,
            OrderSchema.margin2: self._handler.cancel_margin_order,
            OrderSchema.futures: self._handler.futures_cancel_order,
            OrderSchema.futures_coin: self._handler.futures_coin_cancel_order,
        }
        validate_schema(schema, schema_handlers)
        params = utils.map_api_parameter_names({
            'exchange_order_id': int(exchange_order_id),
            'symbol': utils.symbol2stock(symbol),
        })
        data = self._binance_api(schema_handlers[schema.lower()], **params)
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        return utils.load_order_data(data, state_data)

    def get_order(self, exchange_order_id: str, symbol: str, schema: str):
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_order,
            OrderSchema.margin2: self._handler.get_margin_order,
            OrderSchema.futures: self._handler.futures_get_order,
            OrderSchema.futures_coin: self._handler.futures_coin_get_order,
        }
        validate_schema(schema, schema_handlers)
        params = utils.map_api_parameter_names({
            'exchange_order_id': int(exchange_order_id),
            'symbol': utils.symbol2stock(symbol),
        })
        if not (data := self._binance_api(schema_handlers[schema.lower()], **params)):
            return None
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        return utils.load_order_data(data, state_data)

    def list_orders(self, schema: str,
                    symbol: str = None,
                    active_only: bool = True,
                    count: int = None,
                    offset: int = 0,
                    options: dict = None) -> list:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_open_orders, self._handler.get_all_orders),
            OrderSchema.margin2: (self._handler.get_open_margin_orders, self._handler.get_all_margin_orders),
            OrderSchema.futures: (self._handler.futures_get_open_orders, self._handler.futures_get_all_orders),
            OrderSchema.futures_coin: (
                self._handler.futures_coin_get_open_orders, self._handler.futures_coin_get_all_orders
            ),
        }
        validate_schema(schema, schema_handlers)
        state_data = {}
        if options is None:
            options = {}
        if count is not None:
            options['limit'] = count
        if symbol is not None:
            options['symbol'] = utils.symbol2stock(symbol)
            state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        schema = schema.lower()
        if active_only:
            data = self._binance_api(schema_handlers[schema][0], **options)
            return [utils.load_order_data(order, state_data) for order in reversed(data)]
        data = self._binance_api(schema_handlers[schema][1], **options)
        return [utils.load_order_data(order, state_data) for order in reversed(data)][offset:count]

    def list_trades(self, symbol: str, schema: str, **params) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_recent_trades,
            OrderSchema.margin2: self._handler.get_recent_trades,
            OrderSchema.futures: self._handler.futures_recent_trades,
            OrderSchema.futures_coin: self._handler.futures_coin_recent_trades,
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(
            schema_handlers[schema.lower()],
            symbol=symbol.upper(),
            **self._api_kwargs(params),
        )
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        return [utils.load_trade_data(d, state_data) for d in data]

    def close_order(self, exchange_order_id: str, symbol: str, schema: str):
        raise NotImplementedError

    def close_all_orders(self, symbol: str, schema: str):
        raise NotImplementedError

    def get_order_book(
        self,
        symbol: str,
        depth: int = None,
        side: int = None,
        split: bool = False,
        offset: int = 0,
        schema: str = None,
        min_volume_buy: float = None,
        min_volume_sell: float = None,
    ):
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_order_book,
            OrderSchema.margin2: self._handler.get_order_book,
            OrderSchema.futures: self._handler.futures_order_book,
            OrderSchema.futures_coin: self._handler.futures_coin_order_book,
        }
        validate_schema(schema, schema_handlers)
        limit = var.BINANCE_MAX_ORDER_BOOK_LIMIT
        if min_volume_buy is None and min_volume_sell is None:
            if depth:
                for _l in [100, 500, 1000]:
                    if _l >= offset + depth:
                        limit = _l
                        break
        data = self._binance_api(
            schema_handlers[schema.lower()],
            symbol=symbol.upper(),
            limit=limit,
        )
        data = utils.filter_order_book_data(data, min_volume_buy, min_volume_sell)
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), {})
        return utils.load_order_book_data(data, symbol, side, split, offset, depth, state_data)

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', '').lower()
        schema_handlers = {
            OrderSchema.exchange: self._spot_wallet,
            OrderSchema.margin2: self._margin_wallet,
            OrderSchema.futures: self._futures_wallet,
            OrderSchema.futures_coin: self._futures_coin_wallet,
        }
        validate_schema(schema, schema_handlers)
        return schema_handlers[schema](schema=schema, **kwargs)

    def _spot_wallet(self, schema: str, **kwargs):
        is_for_ws = kwargs.pop('is_for_ws', False)
        assets = kwargs.pop('assets', ('btc', 'usd'))
        fields = kwargs.pop('fields', ('balance',))
        data = self._binance_api(self._handler.get_account, **kwargs)
        currencies = self.storage.get('exchange_rates', self.name, schema)
        if is_for_ws:
            fields = ('bl',)
            return utils.load_ws_spot_wallet_data(data, currencies, assets, fields, schema)
        return utils.load_spot_wallet_data(data, currencies, assets, fields, schema)

    def _margin_wallet(self, schema: str, **kwargs):
        is_for_ws = kwargs.pop('is_for_ws', False)
        assets = kwargs.pop('assets', ('btc', 'usd'))
        fields = kwargs.pop('fields', ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed', 'interest'))
        data = self._binance_api(self._handler.get_margin_account, **kwargs)
        currencies = self.storage.get('exchange_rates', self.name, schema)
        if is_for_ws:
            fields = ('bl', 'upnl', 'mbl', 'bor', 'ist')
            return utils.load_ws_margin_wallet_data(data, currencies, assets, fields, schema)
        return utils.load_margin_wallet_data(data, currencies, assets, fields, schema)

    def _futures_wallet(self, schema: str, **kwargs):
        is_for_ws = kwargs.pop('is_for_ws', False)
        assets = kwargs.pop('assets', ('btc', 'usd'))
        fields = kwargs.pop('fields', ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed', 'interest'))
        data = self._binance_api(self._handler.futures_account_v2, **kwargs)
        try:
            cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
        except ConnectorError:
            cross_collaterals = {}
        currencies = self.storage.get('exchange_rates', self.name, schema)
        if is_for_ws:
            fields = ('bl', 'upnl', 'mbl', 'bor', 'ist')
            return utils.load_ws_futures_wallet_data(
                data, currencies, assets, fields, cross_collaterals.get('crossCollaterals', []), schema
            )
        return utils.load_futures_wallet_data(
            data, currencies, assets, fields, cross_collaterals.get('crossCollaterals', []), schema
        )

    def _futures_coin_wallet(self, schema: str, **kwargs):
        is_for_ws = kwargs.pop('is_for_ws', False)
        assets = kwargs.pop('assets', ('btc', 'usd'))
        fields = kwargs.pop('fields', ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed', 'interest'))
        data = self._binance_api(self._handler.futures_coin_account, **kwargs)
        currencies = self.storage.get('exchange_rates', self.name, schema)
        cross_collaterals = []
        if is_for_ws:
            fields = ('bl', 'upnl', 'mbl', 'bor', 'ist')
            return utils.load_ws_futures_coin_wallet_data(
                data, currencies, assets, fields, cross_collaterals, schema
            )
        return utils.load_futures_coin_wallet_data(
            data, currencies, assets, fields, cross_collaterals, schema
        )

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        schema = schema.lower()
        if schema == OrderSchema.exchange:
            _spot = self._binance_api(self._handler.get_account, **kwargs)
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
            }
        try:
            _spot = self._binance_api(self._handler.get_account, **kwargs)
        except ConnectorError:
            _spot = {}
        if schema == OrderSchema.margin2:
            _margin = self._binance_api(self._handler.get_margin_account, **kwargs)
            _borrow = self._binance_api(self._handler.get_max_margin_loan, asset=asset.upper())
            _vip = self.get_vip_level(schema)
            _interest_rate = utils.get_interest_rate(
                self._binance_api(self._handler.get_public_interest_rate, **kwargs),
                _vip, asset
            )
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
                OrderSchema.margin2: utils.load_margin_wallet_detail_data(_margin, asset, _borrow, _interest_rate)
            }
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            schema_handlers = {
                OrderSchema.futures: self._handler.futures_account_v2,
                OrderSchema.futures_coin: self._handler.futures_coin_account,
            }
            _futures = self._binance_api(schema_handlers[schema], **kwargs)
            cross_collaterals = {}
            collateral_configs = []
            if schema == OrderSchema.futures:
                try:
                    cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
                    collateral_configs = self._binance_api(self._handler.futures_loan_configs, loanCoin=asset, **kwargs)
                except ConnectorError:
                    pass
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
                schema: utils.load_futures_wallet_detail_data(
                    _futures, asset, cross_collaterals.get('crossCollaterals', []), collateral_configs
                )
            }

    def get_cross_collaterals(self, schema: str, **kwargs) -> list:
        if schema.lower() == OrderSchema.futures:
            cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
            return utils.load_futures_cross_collaterals_data(cross_collaterals.get('crossCollaterals', []))
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_assets_balance, utils.load_exchange_asset_balance),
            OrderSchema.margin2: (self._handler.get_margin_assets_balance, utils.load_margin_asset_balance),
            OrderSchema.futures: (self._handler.get_futures_assets_balance, utils.load_futures_asset_balance),
            OrderSchema.futures_coin: (
                self._handler.get_futures_coin_assets_balance, utils.load_futures_coin_asset_balance
            ),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        data = self._binance_api(schema_handlers[schema][0])
        return schema_handlers[schema][1](data)

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float) -> dict:
        schemas_handlers = {
            (OrderSchema.exchange, OrderSchema.margin2): self._handler.transfer_spot_to_margin,
            (OrderSchema.exchange, OrderSchema.futures): self._handler.transfer_spot_to_futures,
            (OrderSchema.exchange, OrderSchema.futures_coin): self._handler.transfer_spot_to_futures_coin,
            (OrderSchema.margin2, OrderSchema.exchange): self._handler.transfer_margin_to_spot,
            (OrderSchema.futures, OrderSchema.exchange): self._handler.transfer_futures_to_spot,
            (OrderSchema.futures_coin, OrderSchema.exchange): self._handler.transfer_futures_coin_to_spot,
        }
        try:
            data = self._binance_api(
                schemas_handlers[(from_wallet.lower(), to_wallet.lower())],
                asset=asset.upper(),
                amount=str(amount),
            )
        except KeyError:
            raise ConnectorError(f"Invalid wallet pair {from_wallet} and {to_wallet}.")
        return utils.load_transaction_id(data)

    def wallet_borrow(self, schema: str, asset: str, amount: float, **kwargs):
        if schema.lower() == OrderSchema.margin2:
            data = self._binance_api(self._handler.create_margin_loan, asset=asset.upper(), amount=str(amount))
            return utils.load_transaction_id(data)
        elif schema.lower() == OrderSchema.futures:
            collateral_asset = kwargs.get('collateral_asset', '')
            collateral_amount = kwargs.get('collateral_amount')
            amount_kwargs = {}
            if amount is not None:
                amount_kwargs['amount'] = str(amount)
            if collateral_amount is not None:
                amount_kwargs['collateralAmount'] = str(collateral_amount)
            data = self._binance_api(
                self._handler.create_futures_loan, coin=asset.upper(),
                collateralCoin=collateral_asset.upper(), **amount_kwargs
            )
            return utils.load_borrow_data(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_repay(self, schema: str, asset: str, amount: float, **kwargs):
        if schema.lower() == OrderSchema.margin2:
            data = self._binance_api(self._handler.repay_margin_loan, asset=asset.upper(), amount=str(amount))
        elif schema.lower() == OrderSchema.futures:
            collateral_asset = kwargs.get('collateral_asset', '')
            data = self._binance_api(
                self._handler.repay_futures_loan, coin=asset.upper(),
                amount=str(amount), collateralCoin=collateral_asset.upper()
            )
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return utils.load_repay_data(data)

    def currency_exchange_symbols(self, schema: str, symbol: str = None) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_symbol_ticker,
            OrderSchema.margin2: self._handler.get_symbol_ticker,
            OrderSchema.futures: self._handler.futures_symbol_ticker,
            OrderSchema.futures_coin: self._handler.futures_coin_symbol_ticker,
        }
        validate_schema(schema, schema_handlers)
        currency = self._binance_api(schema_handlers[schema.lower()], symbol=utils.symbol2stock(symbol))
        return utils.load_currency_exchange_symbol(currency)

    def get_symbols_currencies(self, schema: str) -> dict:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_symbol_ticker,
            OrderSchema.margin2: self._handler.get_symbol_ticker,
            OrderSchema.futures: self._handler.futures_symbol_ticker,
            OrderSchema.futures_coin: self._handler.futures_coin_symbol_ticker,
        }
        validate_schema(schema, schema_handlers)
        currency = self._binance_api(schema_handlers[schema.lower()])
        return utils.load_symbols_currencies(currency)

    def get_wallet_summary(self, schemas: iter, **kwargs) -> dict:
        total_summary = {}
        schema_handlers = {
            OrderSchema.exchange: (
                self._handler.get_account,
                utils.load_spot_wallet_balances
            ),
            OrderSchema.margin2: (
                self._handler.get_margin_account,
                utils.load_margin_wallet_balances
            ),
            OrderSchema.futures: (
                self._handler.futures_account_v2,
                utils.load_future_wallet_balances
            ),
            OrderSchema.futures_coin: (
                self._handler.futures_coin_account,
                utils.load_future_coin_wallet_balances
            ),
        }
        if not schemas:
            schemas = schema_handlers.keys()
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance', 'unrealised_pnl', 'margin_balance')
        for schema in schemas:
            schema = schema.lower()
            total_balance = {schema: {}}
            try:
                currencies = self.storage.get('exchange_rates', self.name, schema)
                balances = schema_handlers[schema][1](self._binance_api(schema_handlers[schema][0]))
            except (KeyError, ConnectorError):
                continue
            wallet_summary_in_usd = load_wallet_summary_in_usd(currencies, balances, fields)
            for asset in assets:
                total_balance[schema][asset] = convert_to_currency(
                    wallet_summary_in_usd, currencies.get(utils.to_exchange_asset(asset, schema))
                )
            utils.load_total_wallet_summary(total_summary, total_balance, assets, fields)
        return total_summary

    def list_order_commissions(self, schema: str) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_trade_level,
            OrderSchema.margin2: self._handler.get_trade_level,
            OrderSchema.futures: self._handler.futures_trade_level,
            OrderSchema.futures_coin: self._handler.futures_coin_trade_level,
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(schema_handlers[schema.lower()])
        return utils.load_commissions(data)

    def get_vip_level(self, schema: str) -> str:
        try:
            return utils.get_vip(self._binance_api(self._handler.futures_account_v2))
        except ConnectorError:
            return "0"

    def get_alt_currency_commission(self, schema: str) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        try:
            result = self._binance_api(self._handler.get_bnb_burn_spot_margin)
            is_active = bool(result.get('spotBNBBurn'))
        except ConnectorError:
            is_active = False
        return {
            'is_active': is_active,
            'currency': 'BNB'
        }

    def get_funding_rates(self, symbol: str, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            return []
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            schema_handlers = {
                OrderSchema.futures: self._handler.futures_funding_rate,
                OrderSchema.futures_coin: self._handler.futures_coin_funding_rate,
            }
            funding_rates = self._binance_api(
                schema_handlers[schema],
                symbol=utils.symbol2stock(symbol),
                startTime=int(
                    (
                        datetime.now() - timedelta(hours=period_hour*period_multiplier, minutes=1)
                    ).timestamp() * 1000
                ),
                limit=1000,
            )
            return utils.load_funding_rates(funding_rates)

    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures))
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            return []
        if schema == OrderSchema.futures:
            funding_rates = self._binance_api(
                self._handler.futures_funding_rate,
                startTime=int(
                    (
                        datetime.now() - timedelta(hours=period_hour*period_multiplier, minutes=1)
                    ).timestamp() * 1000
                ),
                limit=1000,
            )
            return utils.load_funding_rates(funding_rates)

    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        validate_schema(schema, (OrderSchema.futures, OrderSchema.futures_coin))
        if schema.lower() == OrderSchema.futures:
            data = self._binance_api(self._handler.futures_position_information, symbol=utils.symbol2stock(symbol))
        else:
            data = self.get_futures_coin_position_data_by_symbol(symbol)
        return utils.load_leverage(data)

    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        schema_handlers = {
            OrderSchema.futures: (
                self._handler.futures_change_margin_type,
                self._handler.futures_change_leverage,
            ),
            OrderSchema.futures_coin: (
                self._handler.futures_coinchange_margin_type,
                self._handler.futures_coin_change_leverage,
            ),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        if kwargs.get('leverage_type_update'):
            self._binance_api(
                schema_handlers[schema][0], symbol=utils.symbol2stock(symbol),
                marginType=utils.store_leverage(leverage_type),
            )
        if kwargs.get('leverage_update'):
            data = self._binance_api(
                schema_handlers[schema][1], symbol=utils.symbol2stock(symbol),
                leverage=int(leverage),
            )
            leverage = utils.to_float(data["leverage"])
        return leverage_type, leverage

    def get_futures_coin_position_data_by_symbol(self, symbol: str) -> list:
        return [d for d in self._binance_api(self._handler.futures_coin_position_information)
                if d.get('symbol', '').upper() == symbol.upper() and
                d.get('positionSide', '').upper() == var.BinancePositionSideMode.BOTH]

    def get_position(self, schema: str, symbol: str, **kwargs) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        schema = schema.lower()
        schema_loaders = {
            OrderSchema.exchange: utils.load_exchange_position,
            OrderSchema.margin2: utils.load_margin2_position,
            OrderSchema.futures: utils.load_futures_position,
            OrderSchema.futures_coin: utils.load_futures_coin_position,
        }
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            try:
                if schema == OrderSchema.futures:
                    data = self._binance_api(self._handler.futures_position_information, symbol=symbol.upper())[0]
                else:
                    data = self.get_futures_coin_position_data_by_symbol(symbol)[0]
            except IndexError:
                return {}
            return schema_loaders[schema](data, schema)
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            data = self.storage.get(
                f"position.{kwargs.get('account_id')}.{self.name}.{schema}.{symbol}".lower()
            )
            symbol_data = self._binance_api(self._handler.get_ticker, symbol=symbol.upper())
            return schema_loaders[schema](data, schema, symbol_data.get('lastPrice'))

    def list_positions(self, schema: str, **kwargs) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        schema = schema.lower()
        if schema in (OrderSchema.futures, OrderSchema.futures_coin):
            schema_handlers = {
                OrderSchema.futures: (self._handler.futures_position_information, utils.load_futures_position_list),
                OrderSchema.futures_coin: (
                    self._handler.futures_coin_position_information, utils.load_futures_coin_position_list
                )
            }
            data = self._binance_api(schema_handlers[schema][0])
            return schema_handlers[schema][1](data, schema)
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            data = self.storage.get_pattern(
                f"position.{kwargs.get('account_id')}.{self.name}.{schema}.*".lower()
            )
            schema_handlers = {
                OrderSchema.exchange: utils.load_exchange_position_list,
                OrderSchema.margin2: utils.load_margin2_position_list,
            }
            symbols_data = self._binance_api(self._handler.get_ticker)
            return schema_handlers[schema](data, schema, symbols_data)

    def _binance_api(self, method: callable, **kwargs):
        try:
            resp = method(**kwargs)
        except HTTPError as exc:
            message = f"Binance api error. Details: {exc.status_code}, {exc.message}"
            if int(exc.status_code) in (418, 429) or int(exc.status_code) >= 500:
                raise RecoverableError(message)
            raise ConnectorError(message)
        except BinanceAPIException as exc:
            message = f"Binance api error. Details: {exc.code}, {exc.message}"
            if int(exc.code) == -2011:
                raise NotFoundError(message)
            raise ConnectorError(message)
        except BinanceRequestException as exc:
            raise ConnectorError(f"Binance api error. Details: {exc.message}")

        self.throttle.set(
            key=self._throttle_hash_name,
            **self.__get_limit_header(self.handler.response.headers)
        )

        if isinstance(resp, dict) and resp.get('code') != 200 and resp.get('msg'):
            try:
                _, msg = resp['msg'].split('=', 1)
            except ValueError:
                msg = resp['msg']
            raise ConnectorError(f"Binance api error. Details: {msg}")
        return resp

    def get_positions_state(self, schema: str) -> dict:
        schema = schema.lower()
        if schema == OrderSchema.futures:
            account_info = self._binance_api(self._handler.futures_account_v2)
            return utils.load_futures_positions_state(account_info)
        if schema == OrderSchema.futures_coin:
            account_info = self._binance_api(self._handler.futures_coin_account)
            state_data = self.storage.get('symbol', self.name, schema)
            return utils.load_futures_coin_positions_state(account_info, state_data)
        return {}

    def get_liquidation(
        self,
        symbol: str,
        schema: str,
        leverage_type: str,
        wallet_balance: float,
        side: int,
        volume: float,
        price: float,
        **kwargs,
    ) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures,
                                 OrderSchema.futures_coin))
        liquidation_price = None
        if schema.lower() in (OrderSchema.futures, OrderSchema.futures_coin):
            positions_state = kwargs.get('positions_state', {})
            _, other_positions_state = BinanceFuturesPositionSerializer.split_positions_state(
                positions_state, symbol,
            )
            leverage_brackets = kwargs.get('leverage_brackets', [])
            maint_margin_sum, unrealised_pnl_sum = BinanceFinFactory.calc_positions_sum(
                schema,
                leverage_type,
                other_positions_state,
                leverage_brackets,
            )
            liquidation_price = BinanceFinFactory.calc_liquidation_price(
                entry_price=price,
                volume=volume,
                side=side,
                leverage_type=leverage_type,
                wallet_balance=wallet_balance,
                leverage_brackets=leverage_brackets,
                maint_margin_sum=maint_margin_sum,
                unrealised_pnl_sum=unrealised_pnl_sum,
                mark_price=kwargs.get('mark_price'),
                schema=schema,
                symbol=symbol,
            )
        return {'liquidation_price': liquidation_price}

    def _api_kwargs(self, kwargs):
        api_kwargs = dict()
        for _k, _v in kwargs.items():
            if _k == 'date_from' and isinstance(_v, datetime):
                api_kwargs['startTime'] = int(_v.timestamp()*1000)
            if _k == 'date_to' and isinstance(_v, datetime):
                api_kwargs['endTime'] = int(_v.timestamp()*1000)
            if _k == 'count':
                api_kwargs['limit'] = _v
        return api_kwargs

    def __get_limit_header(self, headers):
        for h in headers:
            if str(h).upper().startswith('X-MBX-USED-WEIGHT-'):
                rate = h[len('X-MBX-USED-WEIGHT-'):]
                try:
                    return dict(
                        limit=int(headers[h]),
                        reset=self.__parse_reset(rate),
                        scope='rest'
                    )
                except ValueError:
                    pass
            elif str(h).upper().startswith('X-MBX-ORDER-COUNT-'):
                rate = h[len('X-MBX-ORDER-COUNT-'):]
                try:
                    return dict(
                        limit=int(headers[h]),
                        reset=self.__parse_reset(rate),
                        scope='order'
                    )
                except ValueError:
                    pass
        return dict(limit=0, reset=None, scope='rest')

    def __parse_reset(self, rate: str) -> int:
        now = datetime.utcnow()
        if len(rate) < 2:
            return int((now + timedelta(seconds=(60 - now.second))).timestamp())
        try:
            num = int(rate[:-1])
        except ValueError:
            num = 1
        period = rate[len(rate)-1:]
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}.get(period.lower(), 60)
        return int((now + timedelta(seconds=((num * duration) - now.second))).timestamp())
