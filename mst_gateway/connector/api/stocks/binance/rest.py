import httpx
from hashlib import sha256
from datetime import datetime, timedelta
from typing import Union, Tuple, Optional
from mst_gateway.connector.api.utils import time2timestamp
from mst_gateway.storage import StateStorageKey
from mst_gateway.calculator import BinanceFinFactory
from mst_gateway.connector.api.types import OrderSchema, OrderType, ExchangeDrivers
from mst_gateway.connector.api.utils.rest import validate_exchange_order_id, validate_schema
from mst_gateway.connector.api.stocks.binance.lib.exceptions import BinanceAPIException
from mst_gateway.connector.api.stocks.binance.lib.sync_client import BinanceApiClient
from . import utils, var
from .converter import BinanceOrderTypeConverter
from ... import PositionSide, PositionMode
from ...rest import StockRestApi
from .....exceptions import GatewayError, ConnectorError, RecoverableError, NotFoundError, SuccessFullError
from ...rest.throttle import ThrottleRest


class BinanceRestApi(StockRestApi):
    driver = ExchangeDrivers.binance
    name = 'binance'
    fin_factory = BinanceFinFactory()
    throttle = ThrottleRest(rest_limit=var.BINANCE_THROTTLE_LIMITS.get('rest'),
                            order_limit=var.BINANCE_THROTTLE_LIMITS.get('order'))

    def throttle_hash_name(self, url=httpx.URL, **kwargs):
        return sha256(f"{url.host}".lower().encode('utf-8')).hexdigest()

    def _generate_hashed_uid(self):
        return sha256(self.auth.get('api_key').encode('utf-8')).hexdigest()

    def _connect(self, **kwargs):
        return BinanceApiClient(api_key=self._auth.get('api_key'),
                                api_secret=self._auth.get('api_secret'),
                                testnet=self.test)

    def ping(self, schema: str) -> bool:
        schema_handlers = {
            OrderSchema.exchange: self._handler.ping,
            OrderSchema.margin_cross: self._handler.margin_ping,
            OrderSchema.margin_isolated: self._handler.isolated_margin_ping,
            OrderSchema.margin: self._handler.futures_ping,
            OrderSchema.margin_coin: self._handler.futures_coin_ping,
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
            data = {'address': self._generate_hashed_uid()}
        return utils.load_user_data(data)

    def get_api_key_permissions(self, schemas: list, **kwargs) -> Tuple[dict, Optional[int]]:
        auth_expired = None
        default_schemas = [
            OrderSchema.exchange,
            OrderSchema.margin_cross,
            OrderSchema.margin_isolated,
            OrderSchema.margin,
            OrderSchema.margin_coin,
        ]
        permissions = {schema: False for schema in schemas if schema in default_schemas}
        if self.test:
            for schema in permissions:
                try:
                    permissions[schema] = bool(self.get_wallet(schema=schema))
                except ConnectorError:
                    continue
            return permissions, auth_expired
        try:
            data = self._binance_api(self._handler.get_api_key_permission)
            if expiration_timestamp := data.get('tradingAuthorityExpirationTime'):
                auth_expired = utils.to_date(expiration_timestamp)
        except ConnectorError:
            return permissions, auth_expired
        return utils.load_api_key_permissions(data, permissions.keys()), auth_expired

    def get_symbol(self, symbol, schema) -> dict:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_ticker, self._spot_get_symbols_handler),
            OrderSchema.margin_cross: (self._handler.get_margin_ticker, self._spot_get_symbols_handler),
            OrderSchema.margin_isolated: (self._handler.get_isolated_margin_ticker, self._spot_get_symbols_handler),
            OrderSchema.margin: (self._handler.get_futures_ticker, self._futures_get_symbols_handler),
            OrderSchema.margin_coin: (self._handler.get_futures_coin_ticker, self._futures_get_symbols_handler),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        symbol = symbol.upper()
        data = self._binance_api(schema_handlers[schema][0], symbol=symbol)
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{schema}").get(utils.stock2symbol(symbol), {})
        return schema_handlers[schema][1](schema, symbol, data, state_data)

    @staticmethod
    def _spot_get_symbols_handler(schema, symbol, data, state_data):
        return utils.load_symbol_data(schema, data, state_data)

    def _futures_get_symbols_handler(self, schema, symbol, data, state_data):
        schema_handlers = {
            OrderSchema.margin: (
                self._handler.get_futures_order_book_ticker,
                self._handler.get_futures_premium_index,
            ),
            OrderSchema.margin_coin: (
                self._handler.get_futures_coin_order_book_ticker,
                self._handler.get_futures_coin_premium_index,
            ),
        }
        if isinstance(data, list):
            data = data[0]
        try:
            data_bid_ask_price = self._binance_api(schema_handlers[schema][0], symbol=symbol)
        except GatewayError:
            data_bid_ask_price = {}
        if isinstance(data_bid_ask_price, list):
            data_bid_ask_price = data_bid_ask_price[0]
        try:
            data_premium_index = self._binance_api(schema_handlers[schema][1], symbol=symbol)
        except GatewayError:
            data_premium_index = {}
        if isinstance(data_premium_index, list):
            data_premium_index = data_premium_index[0]
        data.update({
            'bidPrice': data_bid_ask_price.get('bidPrice'),
            'askPrice': data_bid_ask_price.get('askPrice'),
            'markPrice': data_premium_index.get('markPrice'),
            'lastFundingRate': data_premium_index.get('lastFundingRate')
        })
        return utils.load_futures_symbol_data(schema, data, state_data)

    @staticmethod
    def _update_ticker_data(ticker_data: list, bid_ask_prices: dict, premium_index: dict) -> dict:
        data = {}
        for ticker in ticker_data:
            symbol = ticker['symbol'].lower()
            bid_ask_price = bid_ask_prices.get(symbol, {})
            premium_index = premium_index.get(symbol, {})
            ticker.update({
                'bidPrice': bid_ask_price.get('bidPrice'),
                'askPrice': bid_ask_price.get('askPrice'),
                'markPrice': premium_index.get('markPrice'),
                'lastFundingRate': premium_index.get('lastFundingRate')
            })
            data[symbol] = ticker
        return data

    def list_symbols(self, schema, **kwargs) -> list:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_ticker, self._spot_list_symbols_handler),
            OrderSchema.margin_cross: (self._handler.get_margin_ticker, self._spot_list_symbols_handler),
            OrderSchema.margin_isolated: (self._handler.get_isolated_margin_ticker, self._spot_list_symbols_handler),
            OrderSchema.margin: (self._handler.get_futures_ticker, self._futures_list_symbols_handler),
            OrderSchema.margin_coin: (self._handler.get_futures_coin_ticker, self._futures_list_symbols_handler),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        data = self._binance_api(schema_handlers[schema][0])
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}")
        return schema_handlers[schema][1](schema, data, state_data)

    @staticmethod
    def _spot_list_symbols_handler(schema, raw_data, state_data):
        data = {data.get('symbol').lower(): data for data in raw_data}
        return [utils.load_symbol_data(schema, data.get(symbol.lower()), st_data)
                for symbol, st_data in state_data.items()]

    def _futures_list_symbols_handler(self, schema, data, state_data):
        schema_handlers = {
            OrderSchema.margin: (
                self._handler.get_futures_order_book_ticker,
                self._handler.get_futures_premium_index,
            ),
            OrderSchema.margin_coin: (
                self._handler.get_futures_coin_order_book_ticker,
                self._handler.get_futures_coin_premium_index,
            ),
        }
        bid_ask_prices = {bap['symbol'].lower(): bap for bap in self._binance_api(schema_handlers[schema][0])}
        premium_index = {pi['symbol'].lower(): pi for pi in self._binance_api(schema_handlers[schema][1])}
        data = self._update_ticker_data(data, bid_ask_prices, premium_index)
        return [utils.load_futures_symbol_data(schema, data.get(symbol.lower(), {}), st_data)
                for symbol, st_data in state_data.items()]

    def get_exchange_symbol_info(self, schema: str) -> list:
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated):
            valid_symbols = None
            data = self._binance_api(self._handler.get_exchange_info)
            if schema == OrderSchema.margin_cross:
                valid_symbols = [
                    symbol.get('symbol') for symbol in self._binance_api(self._handler.get_all_margin_symbols)
                ]
            elif schema == OrderSchema.margin_isolated:
                valid_symbols = [
                    symbol.get('symbol') for symbol in self._binance_api(self._handler.get_all_isolated_margin_symbols)
                ]
            return utils.load_exchange_symbol_info(data.get('symbols', []), schema, valid_symbols)
        if schema in (OrderSchema.margin, OrderSchema.margin_coin):
            schema_handlers = {
                OrderSchema.margin: (
                    self._handler.get_futures_exchange_info,
                    self._handler.get_futures_leverage_bracket,
                    utils.load_futures_exchange_symbol_info,
                    utils.load_futures_leverage_brackets_as_dict
                ),
                OrderSchema.margin_coin: (
                    self._handler.get_futures_coin_exchange_info,
                    self._handler.get_futures_coin_leverage_bracket,
                    utils.load_futures_coin_exchange_symbol_info,
                    utils.load_futures_coin_leverage_brackets_as_dict
                ),
            }
            data = self._binance_api(schema_handlers[schema][0])
            leverage_data = self._binance_api(schema_handlers[schema][1])
            return schema_handlers[schema][2](
                data.get('symbols', []), schema_handlers[schema][3](leverage_data)
            )
        raise ConnectorError(f"Invalid schema {schema}.")

    def _list_quote_bins_page(self, symbol: str, schema: str, binsize: str = '1m', count: int = 100, **kwargs):
        state_data = kwargs.pop('state_data', {})
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_klines,
            OrderSchema.margin_cross: self._handler.get_margin_klines,
            OrderSchema.margin_isolated: self._handler.get_isolated_margin_klines,
            OrderSchema.margin: self._handler.get_futures_klines,
            OrderSchema.margin_coin: self._handler.get_futures_coin_klines,
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
        pages = count // var.BINANCE_MAX_QUOTE_BINS_COUNT + 1
        pages_mod = count % var.BINANCE_MAX_QUOTE_BINS_COUNT or var.BINANCE_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        kwargs = self._api_kwargs(kwargs)
        kwargs['state_data'] = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        for i in range(pages):
            if i == pages - 1:
                items_count = pages_mod
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
                kwargs['startTime'] = int(time2timestamp(quotes[-1].get('time')) + 1)
                quote_bins.extend(quotes)
            else:
                kwargs['endTime'] = int(time2timestamp(quotes[0].get('time')) - 1)
                quotes.extend(quote_bins)
                quote_bins = quotes
        return quote_bins

    def create_order(self, symbol: str, schema: str, side: int, volume: float, order_type: str = OrderType.market,
                     price: float = None, options: dict = None, position_side: str = PositionSide.both) -> dict:
        schema_handlers = {
            OrderSchema.exchange: self._handler.create_order,
            OrderSchema.margin_cross: self._handler.create_margin_order,
            OrderSchema.margin_isolated: self._handler.create_isolated_margin_order,
            OrderSchema.margin: self._handler.create_futures_order,
            OrderSchema.margin_coin: self._handler.create_futures_coin_order,
        }
        validate_schema(schema, schema_handlers)
        # TODO: refactor order request and response data mapping
        main_params = {
            'symbol': utils.symbol2stock(symbol),
            'order_type': order_type,
            'side': utils.store_order_side(side),
            'position_side': position_side.upper(),
            'volume': volume,
            'price': str(price) if price else None,
        }
        params = utils.generate_parameters_by_order_type(main_params, options, schema)
        data = BinanceOrderTypeConverter.prefetch_response_data(
            schema, self._binance_api(schema_handlers[schema.lower()], **params))
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        return utils.load_order_data(schema, data, state_data)

    def update_order(self, exchange_order_id: str, symbol: str, schema: str, side: int, volume: float,
                     order_type: str = OrderType.market, price: float = None, options: dict = None,
                     position_side: str = PositionSide.both) -> dict:
        """
        Updates an order by deleting an existing order and creating a new one.

        """
        self.cancel_order(exchange_order_id, symbol, schema)
        return self.create_order(symbol, schema, side, volume, order_type, price, options=options,
                                 position_side=position_side)

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
            OrderSchema.margin_cross: self._handler.cancel_margin_order,
            OrderSchema.margin_isolated: self._handler.cancel_isolated_margin_order,
            OrderSchema.margin: self._handler.cancel_futures_order,
            OrderSchema.margin_coin: self._handler.cancel_futures_coin_order,
        }
        validate_schema(schema, schema_handlers)
        params = utils.map_api_parameter_names(
            schema,
            {'exchange_order_id': int(exchange_order_id), 'symbol': utils.symbol2stock(symbol)}
        )
        data = BinanceOrderTypeConverter.prefetch_response_data(
            schema, self._binance_api(schema_handlers[schema.lower()], **params))
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        return utils.load_order_data(schema, data, state_data)

    def get_order(self, exchange_order_id: str, symbol: str, schema: str):
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_order,
            OrderSchema.margin_cross: self._handler.get_margin_order,
            OrderSchema.margin_isolated: self._handler.get_isolated_margin_order,
            OrderSchema.margin: self._handler.get_futures_order,
            OrderSchema.margin_coin: self._handler.get_futures_coin_order,
        }
        validate_schema(schema, schema_handlers)
        params = utils.map_api_parameter_names(
            schema,
            {'exchange_order_id': int(exchange_order_id), 'symbol': utils.symbol2stock(symbol)}
        )
        if not (data := self._binance_api(schema_handlers[schema.lower()], **params)):
            return None
        data = BinanceOrderTypeConverter.prefetch_response_data(schema, data)
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        return utils.load_order_data(schema, data, state_data)

    def list_orders(self, schema: str, symbol: str = None, active_only: bool = True,
                    count: int = None, offset: int = 0) -> list:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_open_orders, self._handler.get_all_orders),
            OrderSchema.margin_cross: (self._handler.get_open_margin_orders, self._handler.get_all_margin_orders),
            OrderSchema.margin_isolated: (self._handler.get_open_isolated_margin_orders,
                                          self._handler.get_all_isolated_margin_orders),
            OrderSchema.margin: (self._handler.get_open_futures_orders, self._handler.get_all_futures_orders),
            OrderSchema.margin_coin: (
                self._handler.get_open_futures_coin_orders, self._handler.get_all_futures_coin_orders
            ),
        }
        validate_schema(schema, schema_handlers)
        state_data = {}
        options = {}
        if count is not None:
            options['limit'] = count
        if symbol is not None:
            options['symbol'] = utils.symbol2stock(symbol)
            state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        schema = schema.lower()
        if active_only:
            data = self._binance_api(schema_handlers[schema][0], **options)
            _orders = []
            for order in reversed(data):
                order = BinanceOrderTypeConverter.prefetch_response_data(schema, order)
                _orders.append(utils.load_order_data(schema, order, state_data))
            return _orders
        data = self._binance_api(schema_handlers[schema][1], **options)
        _orders = []
        for order in reversed(data):
            order = BinanceOrderTypeConverter.prefetch_response_data(schema, order)
            _orders.append(utils.load_order_data(schema, order, state_data))
        return _orders[offset:count]

    def list_trades(self, symbol: str, schema: str, **params) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_trades,
            OrderSchema.margin_cross: self._handler.get_margin_trades,
            OrderSchema.margin_isolated: self._handler.get_isolated_margin_trades,
            OrderSchema.margin: self._handler.get_futures_trades,
            OrderSchema.margin_coin: self._handler.get_futures_coin_trades,
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(
            schema_handlers[schema.lower()],
            symbol=symbol.upper(),
            **self._api_kwargs(params),
        )
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
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
            OrderSchema.margin_cross: self._handler.get_margin_order_book,
            OrderSchema.margin_isolated: self._handler.get_isolated_margin_order_book,
            OrderSchema.margin: self._handler.get_futures_order_book,
            OrderSchema.margin_coin: self._handler.get_futures_coin_order_book,
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
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), {})
        return utils.load_order_book_data(data, symbol, side, split, offset, depth, state_data)

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', '').lower()
        schema_handlers = {
            OrderSchema.exchange: self._spot_wallet,
            OrderSchema.margin_cross: self._cross_margin_wallet,
            OrderSchema.margin_isolated: self._isolated_margin_wallet,
            OrderSchema.margin: self._futures_wallet,
            OrderSchema.margin_coin: self._futures_coin_wallet,
        }
        validate_schema(schema, schema_handlers)
        return schema_handlers[schema](**kwargs)

    def _spot_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_account, **kwargs)
        return utils.load_spot_wallet_data(data)

    def _cross_margin_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_margin_account, **kwargs)
        return utils.load_margin_cross_wallet_data(data)

    def _isolated_margin_wallet(self, **kwargs):
        # TODO: refactor by new structures
        data = self._binance_api(self._handler.get_isolated_margin_account, **kwargs)
        return utils.load_margin_isolated_wallet_data(data)

    def _futures_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_futures_account, **kwargs)
        try:
            cross_collaterals = self._binance_api(self._handler.get_futures_loan_wallet, **kwargs)
        except ConnectorError:
            cross_collaterals = {}
        return utils.load_futures_wallet_data(data, cross_collaterals.get('crossCollaterals', []))

    def _futures_coin_wallet(self, **kwargs):
        data = self._binance_api(self._handler.get_futures_coin_account, **kwargs)
        return utils.load_futures_coin_wallet_data(data)

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_account, utils.load_spot_wallet_detail_data),
            OrderSchema.margin_cross: (self._handler.get_margin_account, utils.load_margin_cross_wallet_detail_data),
            # TODO: refactor margin_isolated schema
            # OrderSchema.margin_isolated: (self._handler.get_isolated_margin_account, utils.isolated_margin_balance_data),
            OrderSchema.margin: (self._handler.get_futures_account, utils.load_futures_wallet_detail_data),
            OrderSchema.margin_coin: (self._handler.get_futures_coin_account, utils.load_futures_wallet_detail_data)
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(schema_handlers[schema][0], **kwargs)
        return schema_handlers[schema][1](data, asset)

    def get_wallet_extra_data(self, schema: str, **kwargs) -> dict:
        if schema == OrderSchema.margin:
            try:
                cross_collaterals = self._binance_api(self._handler.get_futures_loan_wallet, **kwargs)
            except ConnectorError:
                return {}
            return {'cross_collaterals': utils.load_margin_cross_collaterals_data(cross_collaterals)}
        return {}

    def get_wallet_detail_extra_data(self, schema: str, asset: str, **kwargs) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated,
                                 OrderSchema.margin, OrderSchema.margin_coin))
        if schema == OrderSchema.margin_cross:
            _margin = self._binance_api(self._handler.get_margin_account, **kwargs)
            try:
                _borrow = self._binance_api(self._handler.get_max_margin_loan, asset=asset.upper())
            except ConnectorError:
                _borrow = None
            _vip = self.get_vip_level(schema)
            try:
                _interest_rate = utils.get_interest_rate(
                    self._binance_api(self._handler.get_public_interest_rate, **kwargs),
                    _vip, asset
                )
            except ConnectorError:
                _interest_rate = None
            return utils.load_margin_cross_wallet_extra_data(_margin, asset, _borrow, _interest_rate)
        if schema == OrderSchema.margin:
            try:
                cross_collaterals = self._binance_api(self._handler.get_futures_loan_wallet)
                collateral_configs = self._binance_api(self._handler.get_futures_loan_configs,
                                                       loanCoin=asset.upper())
            except ConnectorError:
                cross_collaterals = {}
                collateral_configs = []
            return utils.load_futures_wallet_extra_data(cross_collaterals, collateral_configs, asset)
        return {}

    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        schema_handlers = {
            OrderSchema.exchange: (self._handler.get_assets_balance, utils.load_exchange_asset_balance),
            OrderSchema.margin_cross: (self._handler.get_margin_assets_balance, utils.load_margin_cross_asset_balance),
            OrderSchema.margin_isolated: (self._handler.get_isolated_margin_assets_balance,
                                          utils.load_margin_cross_asset_balance),
            OrderSchema.margin: (self._handler.get_futures_assets_balance, utils.load_futures_asset_balance),
            OrderSchema.margin_coin: (self._handler.get_futures_coin_assets_balance,
                                      utils.load_futures_coin_asset_balance),
        }
        validate_schema(schema, schema_handlers)
        schema = schema.lower()
        data = self._binance_api(schema_handlers[schema][0])
        return schema_handlers[schema][1](data)

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float, symbol: str = None) -> dict:
        schemas_handlers = {
            (OrderSchema.exchange, OrderSchema.margin_cross): self._handler.transfer_spot_to_margin,
            (OrderSchema.exchange, OrderSchema.margin_isolated): self._handler.transfer_spot_to_isolated_margin,
            (OrderSchema.exchange, OrderSchema.margin): self._handler.transfer_spot_to_futures,
            (OrderSchema.exchange, OrderSchema.margin_coin): self._handler.transfer_spot_to_futures_coin,
            (OrderSchema.margin_cross, OrderSchema.exchange): self._handler.transfer_margin_to_spot,
            (OrderSchema.margin_isolated, OrderSchema.exchange): self._handler.transfer_isolated_margin_to_spot,
            (OrderSchema.margin, OrderSchema.exchange): self._handler.transfer_futures_to_spot,
            (OrderSchema.margin_coin, OrderSchema.exchange): self._handler.transfer_futures_coin_to_spot
        }
        try:
            data = self._binance_api(
                schemas_handlers[(from_wallet.lower(), to_wallet.lower())],
                asset=asset.upper(),
                amount=amount,
                symbol=symbol
            )
        except KeyError:
            raise ConnectorError(f"Invalid wallet pair {from_wallet} and {to_wallet}.")
        return utils.load_transaction_id(data)

    def wallet_borrow(self, schema: str, asset: str, amount: float, **kwargs):
        if schema.lower() == OrderSchema.margin_cross:
            data = self._binance_api(self._handler.create_margin_loan, asset=asset.upper(), amount=amount)
            return utils.load_transaction_id(data)
        if schema.lower() == OrderSchema.margin_isolated:
            symbol = kwargs.get('symbol')
            data = self._binance_api(
                self._handler.create_isolated_margin_loan,
                asset=asset.upper(),
                amount=amount,
                symbol=symbol.upper()
            )
            return utils.load_transaction_id(data)
        elif schema.lower() == OrderSchema.margin:
            collateral_asset = kwargs.get('collateral_asset', '')
            collateral_amount = kwargs.get('collateral_amount')
            amount_kwargs = {}
            if amount is not None:
                amount_kwargs['amount'] = amount
            if collateral_amount is not None:
                amount_kwargs['collateralAmount'] = collateral_amount
            data = self._binance_api(
                self._handler.create_futures_loan, coin=asset.upper(),
                collateral_coin=collateral_asset.upper(), **amount_kwargs
            )
            return utils.load_borrow_data(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_repay(self, schema: str, asset: str, amount: float, **kwargs):
        if schema.lower() == OrderSchema.margin_cross:
            data = self._binance_api(self._handler.repay_margin_loan, asset=asset.upper(), amount=amount)
        elif schema.lower() == OrderSchema.margin_isolated:
            symbol = kwargs.get('symbol')
            data = self._binance_api(
                self._handler.repay_isolated_margin_loan,
                asset=asset.upper(),
                amount=amount,
                symbol=symbol.upper()
            )
        elif schema.lower() == OrderSchema.margin:
            collateral_asset = kwargs.get('collateral_asset', '')
            data = self._binance_api(
                self._handler.repay_futures_loan, coin=asset.upper(),
                amount=amount, collateralCoin=collateral_asset.upper()
            )
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return utils.load_repay_data(data)

    def currency_exchange_symbols(self, schema: str, symbol: str = None) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_symbol_ticker,
            OrderSchema.margin_cross: self._handler.get_margin_symbol_ticker,
            OrderSchema.margin: self._handler.get_futures_symbol_ticker,
            OrderSchema.margin_coin: self._handler.get_futures_coin_symbol_ticker,
        }
        validate_schema(schema, schema_handlers)
        currency = self._binance_api(schema_handlers[schema.lower()], symbol=utils.symbol2stock(symbol))
        return utils.load_currency_exchange_symbol(currency)

    def get_symbols_currencies(self, schema: str) -> dict:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_symbol_ticker,
            OrderSchema.margin_cross: self._handler.get_margin_symbol_ticker,
            OrderSchema.margin_isolated: self._handler.get_isolated_margin_symbol_ticker,
            OrderSchema.margin: self._handler.get_futures_symbol_ticker,
            OrderSchema.margin_coin: self._handler.get_futures_coin_symbol_ticker,
        }
        validate_schema(schema, schema_handlers)
        currency = self._binance_api(schema_handlers[schema.lower()])
        return utils.load_symbols_currencies(currency, self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}"))

    def list_order_commissions(self, schema: str) -> list:
        schema_handlers = {
            OrderSchema.exchange: self._handler.get_trade_level,
            OrderSchema.margin_cross: self._handler.get_margin_trade_level,
            OrderSchema.margin: self._handler.get_futures_trade_level,
            OrderSchema.margin_coin: self._handler.get_futures_coin_trade_level,
        }
        validate_schema(schema, schema_handlers)
        data = self._binance_api(schema_handlers[schema.lower()])
        return utils.load_commissions(data)

    def get_vip_level(self, schema: str) -> str:
        try:
            return utils.get_vip(self._binance_api(self._handler.get_futures_account))
        except ConnectorError:
            return "0"

    def get_alt_currency_commission(self, schema: str) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        try:
            result = self._binance_api(self._handler.get_bnb_burn)
            is_active = bool(result.get('spotBNBBurn'))
        except ConnectorError:
            is_active = False
        return {
            'is_active': is_active,
            'currency': 'BNB'
        }

    def get_funding_rates(self, symbol: str, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin_cross):
            return []
        if schema in (OrderSchema.margin, OrderSchema.margin_coin):
            schema_handlers = {
                OrderSchema.margin: self._handler.get_futures_funding_rate,
                OrderSchema.margin_coin: self._handler.get_futures_coin_funding_rate,
            }
            funding_rates = self._binance_api(
                schema_handlers[schema],
                symbol=utils.symbol2stock(symbol),
                startTime=int(
                    (
                            datetime.now() - timedelta(hours=period_hour * period_multiplier, minutes=1)
                    ).timestamp() * 1000
                ),
                limit=1000,
            )
            return utils.load_funding_rates(funding_rates)

    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin))
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin_cross):
            return []
        if schema == OrderSchema.margin:
            funding_rates = self._binance_api(
                self._handler.get_futures_funding_rate,
                startTime=int(
                    (
                            datetime.now() - timedelta(hours=period_hour * period_multiplier, minutes=1)
                    ).timestamp() * 1000
                ),
                limit=1000,
            )
            return utils.load_funding_rates(funding_rates)

    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        validate_schema(schema, (OrderSchema.margin, OrderSchema.margin_coin))
        schema = schema.lower()
        if schema == OrderSchema.margin_coin:
            data = [position for position in self._binance_api(self._handler.get_futures_coin_position_info,
                                                               pair=utils.symbol2pair(symbol))
                    if position.get('symbol').lower() == symbol.lower()]
        else:
            data = self._binance_api(self._handler.get_futures_position_info, symbol=utils.symbol2stock(symbol))
        return utils.load_leverage(data)

    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        schema_handlers = {
            OrderSchema.margin: (
                self._handler.change_futures_margin_type,
                self._handler.change_futures_leverage,
            ),
            OrderSchema.margin_coin: (
                self._handler.change_futures_coin_margin_type,
                self._handler.change_futures_coin_leverage,
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

    def get_position_mode(self, schema: str) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        schema = schema.lower()
        if schema in (OrderSchema.margin, OrderSchema.margin_coin):
            schema_handlers = {
                OrderSchema.margin: self._handler.get_futures_position_mode,
                OrderSchema.margin_coin: self._handler.get_futures_coin_position_mode,
            }
            data = self._binance_api(schema_handlers[schema.lower()])
            return utils.load_position_mode(data)
        return {'mode': PositionMode.one_way}

    def change_position_mode(self, schema: str, mode: str) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        schema = schema.lower()
        if schema in (OrderSchema.exchange, OrderSchema.margin_cross):
            raise ConnectorError('Binance api error. Details: Invalid method.')
        schema_handlers = {
            OrderSchema.margin: self._handler.change_futures_position_mode,
            OrderSchema.margin_coin: self._handler.change_futures_coin_position_mode,
        }
        self._binance_api(schema_handlers[schema], dualSidePosition=utils.store_position_mode(mode))
        return {'mode': mode}

    def get_position(self, schema: str, symbol: str,  position_side: str = PositionSide.both, **kwargs) -> dict:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        schema = schema.lower()
        if schema == OrderSchema.margin_coin:
            for position in self._binance_api(self._handler.get_futures_coin_position_info,
                                              pair=utils.symbol2pair(symbol)):
                if (
                    position.get('symbol', '').lower() == symbol.lower() and
                    position.get('positionSide', '').lower() == position_side.lower()
                ):
                    return utils.load_futures_coin_position(position, schema)
        if schema == OrderSchema.margin:
            for position in self._binance_api(self._handler.get_futures_position_info,
                                              symbol=utils.symbol2stock(symbol)):
                if position.get('positionSide', '').lower() == position_side.lower():
                    return utils.load_futures_position(position, schema)
        return {}

    def list_positions(self, schema: str, **kwargs) -> list:
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        schema = schema.lower()
        if schema in (OrderSchema.margin, OrderSchema.margin_coin):
            schema_handlers = {
                OrderSchema.margin: (self._handler.get_futures_position_info, utils.load_futures_position_list),
                OrderSchema.margin_coin: (
                    self._handler.get_futures_coin_position_info, utils.load_futures_coin_position_list
                )
            }
            data = self._binance_api(schema_handlers[schema][0])
            return schema_handlers[schema][1](data, schema)
        return []

    def get_positions_state(self, schema: str) -> dict:
        schema = schema.lower()
        if schema == OrderSchema.margin:
            account_info = self._binance_api(self._handler.get_futures_account)
            return utils.load_futures_positions_state(account_info, empty_volume=False)
        if schema == OrderSchema.margin_coin:
            account_info = self._binance_api(self._handler.get_futures_coin_account)
            state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}")
            return utils.load_futures_coin_positions_state(account_info, state_data, empty_volume=False)
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
        validate_schema(schema, (OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin,
                                 OrderSchema.margin_coin))
        liquidation_price = None
        if schema.lower() in (OrderSchema.margin, OrderSchema.margin_coin):
            liquidation_price = BinanceFinFactory.calc_liquidation_price(
                side,
                volume,
                price,
                leverage_type,
                wallet_balance,
                schema=schema,
                symbol=symbol,
                position_side=kwargs.get('position_side'),
                mark_price=kwargs.get('mark_price'),
                positions_state=kwargs.get('positions_state', {}),
                leverage_brackets=kwargs.get('leverage_brackets', {})
            )
        return {'liquidation_price': liquidation_price}

    def _binance_api(self, method: callable, **kwargs):
        rest_method, url = self.handler.get_method_info(method.__name__, **kwargs)
        if not rest_method:
            raise ConnectorError('Binance request method error.')
        if not self.ratelimit:
            self.validate_throttling(self.throttle_hash_name(url))
        else:
            try:
                kwargs['proxies'] = self.ratelimit.get_proxies(
                    method=rest_method, url=str(url), hashed_uid=self._generate_hashed_uid()
                )
            except ConnectionError:
                self.logger.warning(f"Proxy list error. {rest_method} {url}")
                raise ConnectorError(f"Proxy list error.")
        try:
            resp = method(**kwargs)
            data = self.handler.handle_response(resp)
        except BinanceAPIException as exc:
            if not self.ratelimit:
                self.throttle.set(
                    key=self.throttle_hash_name(url),
                    **self.__get_limit_header(exc.response.headers)
                )
            message = f"Binance api error. Details: {exc.code}, {exc.message}"
            if exc.code == -1003:
                self.logger.critical(f"{self.__class__.__name__}: {exc}")
            if exc.code == -2011:
                raise NotFoundError(message)
            if exc.code in (-4059, -4046):
                raise SuccessFullError(message, exc.code)
            if exc.status_code in (418, 429) or exc.status_code >= 500:
                raise RecoverableError(message)
            self.logger.warning(f"Binance api error. Detail: {exc}")
            raise ConnectorError(message)
        except Exception as exc:
            self.logger.exception(f"Binance adapter error. Detail: {exc}. Proxies: {kwargs.get('proxies', None)}")
            raise ConnectorError("Binance api error.")
        return data

    def _api_kwargs(self, kwargs):
        api_kwargs = dict()
        for _k, _v in kwargs.items():
            if _k == 'date_from' and isinstance(_v, datetime):
                api_kwargs['startTime'] = int(_v.timestamp() * 1000)
            if _k == 'date_to' and isinstance(_v, datetime):
                api_kwargs['endTime'] = int(_v.timestamp() * 1000)
            if _k == 'count' and _v is not None:
                api_kwargs['limit'] = _v
        return api_kwargs

    def __get_limit_header(self, headers: httpx.Headers):
        if h := headers.get('retry-after'):
            try:
                retry_after = int(h)
                return dict(
                    limit=float('inf'),
                    reset=self.__parse_reset(retry_after),
                    scope='rest',
                    timeout=retry_after + 10
                )
            except (ValueError, TypeError):
                pass

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

    def __parse_reset(self, rate: Union[str, int]) -> int:
        now = datetime.utcnow()
        if isinstance(rate, int):
            return int((now + timedelta(seconds=rate)).timestamp())
        if len(rate) < 2:
            return int((now + timedelta(seconds=(60 - now.second))).timestamp())
        try:
            num = int(rate[:-1])
        except ValueError:
            num = 1
        period = rate[len(rate) - 1:]
        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}.get(period.lower(), 60)
        return int((now + timedelta(seconds=((num * duration) - now.second))).timestamp())
