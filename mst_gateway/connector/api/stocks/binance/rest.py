from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional, Union
from bravado.exception import HTTPError
from binance.exceptions import BinanceAPIException, BinanceRequestException
from mst_gateway.calculator import BinanceFinFactory
from mst_gateway.connector.api.types import OrderSchema, OrderType
from mst_gateway.connector.api.utils.rest import validate_exchange_order_id
from mst_gateway.connector.api.stocks.binance.wss.serializers.position import BinanceFuturesPositionSerializer
from .lib import Client
from . import utils, var
from ...rest import StockRestApi
from .....exceptions import ConnectorError, RecoverableError, NotFoundError


class BinanceRestApi(StockRestApi):
    name = 'binance'
    fin_factory = BinanceFinFactory()

    def _connect(self, **kwargs):
        return Client(api_key=self._auth.get('api_key'),
                      api_secret=self._auth.get('api_secret'),
                      test=self.test)

    def ping(self) -> bool:
        try:
            self._binance_api(self._handler.ping)
        except ConnectorError:
            return False
        return True

    def get_user(self) -> dict:
        try:
            data = self._binance_api(self._handler.get_deposit_address, asset='eth')
        except ConnectorError as e:
            if not self.name.startswith('t'):
                raise ConnectorError(e)
            data = {'address': uuid4()}
        return utils.load_user_data(data)

    def get_symbol(self, symbol, schema) -> dict:
        if schema == OrderSchema.futures:
            data_ticker = self._binance_api(self._handler.futures_ticker, symbol=symbol.upper())
            data_bid_ask_price = self._binance_api(self._handler.futures_orderbook_ticker, symbol=symbol.upper())
            data = {
                'bidPrice': data_bid_ask_price.get('bidPrice'),
                'askPrice': data_bid_ask_price.get('askPrice'),
                **data_ticker
            }
        elif schema in (OrderSchema.margin2, OrderSchema.exchange):
            data = self._binance_api(self._handler.get_ticker, symbol=symbol.upper())
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        state_data = self.storage.get(
            'symbol', self.name, schema
        ).get(utils.stock2symbol(symbol), dict())
        return utils.load_symbol_data(data, state_data)

    def list_symbols(self, schema, **kwargs) -> list:
        state_data = self.storage.get(
            'symbol', self.name, schema
        )
        if schema == OrderSchema.futures:
            _param = None
            data = self._binance_api(self._handler.futures_ticker)
        elif schema in (OrderSchema.margin2, OrderSchema.exchange):
            _param = 'weightedAvgPrice'
            data = self._binance_api(self._handler.get_ticker)
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        symbols = []
        for d in data:
            symbol_state = state_data.get(d.get('symbol').lower())
            if symbol_state and (not _param or (_param and utils.to_float(d[_param]))):
                symbols.append(utils.load_symbol_data(d, symbol_state))
        return symbols

    def get_exchange_symbol_info(self, schema: str) -> list:
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            data = self._binance_api(self._handler.get_exchange_info)
            return utils.load_exchange_symbol_info(data.get('symbols', []))
        elif schema == OrderSchema.futures:
            data = self._binance_api(self._handler.futures_exchange_info)
            leverage_data = self._binance_api(self._handler.futures_leverage_bracket)
            return utils.load_futures_exchange_symbol_info(
                data.get('symbols', []), utils.load_futures_leverage_brackets_as_dict(leverage_data)
            )
        else:
            raise ConnectorError(f"Invalid schema {schema}.")

    def get_quote(self, symbol: str, timeframe: str = None, **kwargs) -> dict:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol.upper(), limit=1)
        state_data = self.storage.get(
            'symbol', self.name, kwargs.get('schema')
        ).get(symbol.lower(), dict())
        return utils.load_quote_data(data[0], state_data)

    def list_quotes(self, symbol: str, timeframe: str = None, **kwargs) -> list:
        data = self._binance_api(self._handler.get_historical_trades, symbol=symbol.upper())
        state_data = self.storage.get(
            'symbol', self.name, kwargs.get('schema')
        ).get(symbol.lower(), dict())
        return [utils.load_quote_data(d, state_data) for d in data]

    def _list_quote_bins_page(self, symbol, schema, binsize='1m', count=100, **kwargs):
        state_data = kwargs.pop('state_data', dict())
        if schema == OrderSchema.futures:
            data = self._binance_api(
                self._handler.futures_klines, symbol=symbol.upper(), interval=binsize, limit=count, **kwargs
            )
            return [utils.load_quote_bin_data(d, state_data) for d in data]
        elif schema in (OrderSchema.margin2, OrderSchema.exchange):
            data = self._binance_api(
                self._handler.get_klines, symbol=symbol.upper(), interval=binsize, limit=count, **kwargs
            )
            return [utils.load_quote_bin_data(d, state_data) for d in data]
        else:
            raise ConnectorError(f"Invalid schema {schema}.")

    def list_quote_bins(self, symbol, schema, binsize='1m', count=100, **kwargs) -> list:
        pages = int((count - 1) / var.BINANCE_MAX_QUOTE_BINS_COUNT + 1)
        rest = count % var.BINANCE_MAX_QUOTE_BINS_COUNT or var.BINANCE_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        kwargs = self._api_kwargs(kwargs)
        kwargs['state_data'] = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
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
        params = dict(
            symbol=utils.symbol2stock(symbol),
            order_type=order_type,
            side=utils.store_order_side(side),
            volume=volume,
            price=str(price)
        )
        params = utils.generate_parameters_by_order_type(params, options, schema)
        schema_handlers = {
            OrderSchema.exchange: self._handler.create_order,
            OrderSchema.margin2: self._handler.create_margin_order,
            OrderSchema.futures: self._handler.futures_create_order,
        }
        if schema not in schema_handlers:
            raise ConnectorError(f"Invalid schema parameter: {schema}")

        data = self._binance_api(schema_handlers[schema], **params)
        state_data = self.storage.get('symbol', self.name, schema).get(
            symbol.lower(), dict())
        return utils.load_order_data(data, state_data)

    def update_order(self, exchange_order_id: str, symbol: str,
                     schema: str, side: int, volume: float,
                     order_type: str = OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        """
        Updates an order by deleting an existing order and creating a new one.

        """
        self.cancel_order(exchange_order_id, symbol, schema)
        return self.create_order(symbol, schema, side, volume,
                                 order_type, price, options=options)

    def cancel_all_orders(self, schema: str):
        open_orders = [dict(symbol=order["symbol"], orderId=order["orderId"]) for order in
                       self._binance_api(self._handler.get_open_orders)]
        data = [self._binance_api(self._handler.cancel_order, **order) for order in open_orders]
        return bool(data)

    def cancel_order(self, exchange_order_id: str, symbol: str, schema: str) -> dict:
        validate_exchange_order_id(exchange_order_id)
        params = dict(
            exchange_order_id=int(exchange_order_id),
            symbol=utils.symbol2stock(symbol)
        )
        params = utils.map_api_parameter_names(params)
        schema_handlers = {
            OrderSchema.exchange: self._handler.cancel_order,
            OrderSchema.margin2: self._handler.cancel_margin_order,
            OrderSchema.futures: self._handler.futures_cancel_order,
        }
        if schema not in schema_handlers:
            raise ConnectorError(f"Invalid schema parameter: {schema}")

        data = self._binance_api(schema_handlers[schema], **params)
        return data

    def get_order(self, exchange_order_id: str, symbol: str, schema: str):
        params = dict(
            exchange_order_id=int(exchange_order_id),
            symbol=utils.symbol2stock(symbol)
        )
        params = utils.map_api_parameter_names(params)

        schema_handlers = {
            OrderSchema.exchange: self._handler.get_order,
            OrderSchema.margin2: self._handler.get_margin_order,
            OrderSchema.futures: self._handler.futures_get_order,
        }
        if schema not in schema_handlers:
            raise ConnectorError(f"Invalid schema parameter: {schema}")

        data = self._binance_api(schema_handlers[schema], **params)
        if not data:
            return None

        state_data = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
        return utils.load_order_data(data, state_data)

    def list_orders(self, schema: str, symbol: str,
                    active_only: bool = True,
                    count: int = None,
                    offset: int = 0,
                    params: dict = None) -> list:
        if params is None:
            params = {}
        if active_only:
            data = self._binance_api(self._handler.get_open_orders, **params)
            return [utils.load_order_data(d, dict()) for d in data]
        if count is not None:
            params['limit'] = count
        data = self._binance_api(self._handler.get_all_orders, **params)
        return [utils.load_order_data(d, dict()) for d in data][offset:count]

    def list_trades(self, symbol: str, schema: str, **params) -> list:
        state_data = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            data = self._binance_api(self._handler.get_recent_trades, symbol=symbol.upper(),
                                     **self._api_kwargs(params))
        elif schema == OrderSchema.futures:
            data = self._binance_api(self._handler.futures_recent_trades, symbol=symbol.upper(),
                                     **self._api_kwargs(params))
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
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
        state_data = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
        limit = var.BINANCE_MAX_ORDER_BOOK_LIMIT
        if min_volume_buy is None and min_volume_sell is None:
            if depth:
                for _l in [100, 500, 1000]:
                    if _l >= offset + depth:
                        limit = _l
                        break

        if schema == OrderSchema.futures:
            data = self._binance_api(self._handler.futures_order_book, symbol=symbol.upper(),
                                     limit=limit)
        elif schema in (OrderSchema.margin2, OrderSchema.exchange):
            data = self._binance_api(self._handler.get_order_book, symbol=symbol.upper(),
                                     limit=limit)
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        data = utils.filter_order_book_data(data, min_volume_buy, min_volume_sell)
        return utils.load_order_book_data(data, symbol, side, split, offset, depth, state_data)

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', '').lower()
        if schema == OrderSchema.exchange:
            return self._spot_wallet(**kwargs)
        if schema == OrderSchema.margin2:
            return self._margin_wallet(**kwargs)
        if schema == OrderSchema.futures:
            return self._futures_wallet(**kwargs)
        raise ConnectorError(f"Invalid schema {schema}.")

    def _spot_wallet(self, **kwargs):
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance',)
        data = self._binance_api(self._handler.get_account, **kwargs)
        currencies = self.storage.get('currency', self.name, OrderSchema.exchange)
        return utils.load_spot_wallet_data(data, currencies, assets, fields)

    def _margin_wallet(self, **kwargs):
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed', 'interest')
        data = self._binance_api(self._handler.get_margin_account, **kwargs)
        currencies = self.storage.get('currency', self.name, OrderSchema.margin2)
        return utils.load_margin_wallet_data(data, currencies, assets, fields)

    def _futures_wallet(self, **kwargs):
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance', 'unrealised_pnl', 'margin_balance', 'borrowed', 'interest')
        data = self._binance_api(self._handler.futures_account, **kwargs)
        try:
            cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
        except ConnectorError:
            cross_collaterals = {}
        currencies = self.storage.get('currency', self.name, OrderSchema.futures)
        return utils.load_futures_wallet_data(
            data, currencies, assets, fields, cross_collaterals.get('crossCollaterals', [])
        )

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        if schema.lower() == OrderSchema.exchange:
            _spot = self._binance_api(self._handler.get_account, **kwargs)
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
            }

        try:
            _spot = self._binance_api(self._handler.get_account, **kwargs)
        except ConnectorError:
            _spot = {}
        if schema.lower() == OrderSchema.margin2:
            _margin = self._binance_api(self._handler.get_margin_account, **kwargs)
            _borrow = self._binance_api(self._handler.get_max_margin_loan, asset=asset.upper())
            _vip = self.get_vip_level(schema.lower())
            _interest_rate = utils.get_interest_rate(
                self._binance_api(self._handler.get_public_interest_rate, **kwargs),
                _vip, asset
            )
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
                OrderSchema.margin2: utils.load_margin_wallet_detail_data(_margin, asset, _borrow, _interest_rate)
            }
        if schema.lower() == OrderSchema.futures:
            _futures = self._binance_api(self._handler.futures_account, **kwargs)
            try:
                cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
                collateral_configs = self._binance_api(self._handler.futures_loan_configs, loanCoin=asset, **kwargs)
            except ConnectorError:
                cross_collaterals = {}
                collateral_configs = []
            return {
                OrderSchema.exchange: utils.load_spot_wallet_detail_data(_spot, asset),
                OrderSchema.futures: utils.load_futures_wallet_detail_data(
                    _futures, asset, cross_collaterals.get('crossCollaterals', []), collateral_configs
                )
            }
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_cross_collaterals(self, schema: str, **kwargs) -> list:
        if schema.lower() == OrderSchema.futures:
            cross_collaterals = self._binance_api(self._handler.futures_loan_wallet, **kwargs)
            return utils.load_futures_cross_collaterals_data(cross_collaterals.get('crossCollaterals', []))
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        if schema == OrderSchema.exchange:
            raw_data = self._binance_api(self._handler.get_assets_balance)
            return utils.load_exchange_asset_balance(raw_data)
        if schema == OrderSchema.margin2:
            raw_data = self._binance_api(self._handler.get_margin_assets_balance)
            return utils.load_margin_asset_balance(raw_data)
        if schema == OrderSchema.futures:
            raw_data = self._binance_api(self._handler.get_futures_assets_balance)
            return utils.load_futures_asset_balance(raw_data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float) -> dict:
        if from_wallet.lower() == OrderSchema.exchange and to_wallet.lower() == OrderSchema.margin2:
            method = self._handler.transfer_spot_to_margin
        elif from_wallet.lower() == OrderSchema.margin2 and to_wallet.lower() == OrderSchema.exchange:
            method = self._handler.transfer_margin_to_spot
        elif from_wallet.lower() == OrderSchema.exchange and to_wallet.lower() == OrderSchema.futures:
            method = self._handler.futures_transfer_spot_to_futures
        elif from_wallet.lower() == OrderSchema.futures and to_wallet.lower() == OrderSchema.exchange:
            method = self._handler.futures_transfer_futures_to_spot
        else:
            raise ConnectorError(f"Invalid wallet pair {from_wallet} and {to_wallet}.")
        data = self._binance_api(method, asset=asset.upper(), amount=str(amount))
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
        if schema.lower() in (OrderSchema.exchange, OrderSchema.margin2):
            currency = self._binance_api(self._handler.get_symbol_ticker, symbol=utils.symbol2stock(symbol))
        elif schema.lower() == OrderSchema.futures:
            currency = self._binance_api(self._handler.futures_symbol_ticker, symbol=utils.symbol2stock(symbol))
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return utils.load_currency_exchange_symbol(currency)

    def get_symbols_currencies(self, schema: str) -> dict:
        if schema.lower() in (OrderSchema.exchange, OrderSchema.margin2):
            currency = self._binance_api(self._handler.get_symbol_ticker)
        elif schema.lower() == OrderSchema.futures:
            currency = self._binance_api(self._handler.futures_symbol_ticker)
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return utils.load_symbols_currencies(currency)

    def get_wallet_summary(self, schemas: iter, **kwargs) -> dict:
        if not schemas:
            schemas = (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures)
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance', 'unrealised_pnl', 'margin_balance')

        total_summary = dict()

        currencies = utils.load_currencies_as_dict(self._binance_api(self._handler.get_all_tickers))
        _currencies_f = None
        if OrderSchema.futures in schemas:
            _currencies_f = utils.load_currencies_as_dict(self._binance_api(self._handler.futures_symbol_ticker))

        for schema in schemas:
            total_balance = {schema: {}}
            try:
                if schema == OrderSchema.exchange:
                    balances = utils.load_spot_wallet_balances(self._binance_api(self._handler.get_account))
                    _currencies = currencies
                elif schema == OrderSchema.margin2:
                    balances = utils.load_margin_wallet_balances(self._binance_api(self._handler.get_margin_account))
                    _currencies = currencies
                elif schema == OrderSchema.futures:
                    balances = utils.load_future_wallet_balances(self._binance_api(self._handler.futures_account))
                    _currencies = _currencies_f
                else:
                    continue
            except ConnectorError:
                continue
            for asset in assets:
                total_balance[schema][asset] = utils.load_wallet_summary(_currencies, balances, asset, fields)
            utils.load_total_wallet_summary(total_summary, total_balance, assets, fields)
        return total_summary

    def list_order_commissions(self, schema: str) -> list:
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            commissions = self._binance_api(self._handler.get_trade_level)
        elif schema == OrderSchema.futures:
            commissions = self._binance_api(self._handler.futures_trade_level)
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return utils.load_commissions(commissions)

    def get_vip_level(self, schema: str) -> str:
        try:
            return utils.get_vip(self._binance_api(self._handler.futures_account_v2))
        except ConnectorError:
            return "0"

    def get_alt_currency_commission(self, schema: str) -> dict:
        if schema in (OrderSchema.exchange, OrderSchema.margin2, OrderSchema.futures):
            try:
                result = self._binance_api(self._handler.get_bnb_burn_state)
                is_active = bool(result.get('spotBNBBurn'))
            except ConnectorError:
                is_active = False
        else:
            raise ConnectorError(f"Invalid schema {schema}.")
        return {
            'is_active': is_active,
            'currency': 'BNB'
        }

    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        if schema == OrderSchema.futures:
            funding_rates = self._binance_api(
                self._handler.futures_funding_rate,
                startTime=int(
                    (
                        datetime.now() - timedelta(hours=period_hour*period_multiplier, minutes=1)
                    ).timestamp() * 1000
                ),
                limit=1000
            )
            return utils.load_funding_rates(funding_rates)
        elif schema in (OrderSchema.exchange, OrderSchema.margin2):
            return []
        else:
            raise ConnectorError(f"Invalid schema {schema}.")

    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            raise ConnectorError(f"Unavailable method for {schema}.")
        if schema == OrderSchema.futures:
            response = self._binance_api(self._handler.futures_position_information, symbol=utils.symbol2stock(symbol))
            return utils.load_leverage(response)
        raise ConnectorError(f"Invalid schema {schema}.")

    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        if schema in (OrderSchema.exchange, OrderSchema.margin2):
            raise ConnectorError(f"Unavailable method for {schema}.")
        if schema == OrderSchema.futures:
            if kwargs.get('leverage_type_update'):
                self._binance_api(
                    self._handler.futures_change_margin_type, symbol=utils.symbol2stock(symbol),
                    marginType=utils.store_leverage(leverage_type)
                )
            if kwargs.get('leverage_update'):
                response = self._binance_api(
                    self._handler.futures_change_leverage,
                    symbol=utils.symbol2stock(symbol), leverage=int(leverage),
                )
                leverage = utils.to_float(response["leverage"])
            return leverage_type, leverage
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_position(self, schema: str, symbol: str, **kwargs) -> dict:
        if schema == OrderSchema.futures:
            response = self._binance_api(self._handler.futures_position_information, symbol=symbol.upper())
            try:
                response = response[0]
            except IndexError:
                return {}
            return utils.load_futures_position(response, schema)
        account_id = kwargs.get('account_id')
        position_state_key = f"position.{account_id}.{self.name}.{schema}.{symbol}".lower()
        position = self.storage.get(position_state_key)
        symbol_data = self._binance_api(self._handler.get_ticker, symbol=symbol.upper())
        if schema == OrderSchema.exchange:
            return utils.load_exchange_position(position, schema, symbol_data.get('lastPrice'))
        if schema == OrderSchema.margin2:
            return utils.load_margin2_position(position, schema, symbol_data.get('lastPrice'))
        raise ConnectorError(f"Invalid schema {schema}.")

    def list_positions(self, schema: str, **kwargs) -> list:
        if schema == OrderSchema.futures:
            response = self._binance_api(self._handler.futures_position_information)
            return utils.load_futures_position_list(response, schema)
        account_id = kwargs.get('account_id')
        position_state_key = f"position.{account_id}.{self.name}.{schema}.*".lower()
        positions = self.storage.get_pattern(position_state_key)
        symbol_list = self._binance_api(self._handler.get_ticker)
        if schema == OrderSchema.exchange:
            return utils.load_exchange_position_list(positions, schema, symbol_list)
        if schema == OrderSchema.margin2:
            return utils.load_margin2_position_list(positions, schema, symbol_list)
        raise ConnectorError(f"Invalid schema {schema}.")

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

    def get_positions_state(self, schema):
        positions_state = {}
        if schema == OrderSchema.futures:
            account_info = self._binance_api(self._handler.futures_account_v2)
            positions_state = utils.load_futures_positions_state(account_info)
        return positions_state

    def get_liquidation(
        self,
        symbol: str,
        schema: str,
        leverage_type: str,
        wallet_balance: float,
        side: int,
        volume: float,
        price: float,
        leverage: Optional[float],
        mark_price: Optional[float],
        **kwargs,
    ) -> dict:
        if schema not in (OrderSchema.exchange, OrderSchema.futures, OrderSchema.margin2):
            raise ConnectorError(f'Invalid schema {schema}.')
        liquidation_price = None
        if schema == OrderSchema.futures:
            positions_state = kwargs.get('positions_state', {})
            _, positions_state = BinanceFuturesPositionSerializer.split_positions_state(positions_state, symbol)
            leverage_brackets = kwargs.get('leverage_brackets', [])
            other_positions_maint_margin, other_positions_unrealised_pnl = BinanceFuturesPositionSerializer.calc_other_positions_sum(
                leverage_type, leverage_brackets, positions_state
            )
            liquidation_price = BinanceFuturesPositionSerializer.calc_liquidation_price(
                entry_price=price,
                mark_price=mark_price,
                volume=volume,
                side=side,
                leverage_type=leverage_type,
                position_margin=wallet_balance,
                leverage_brackets=leverage_brackets,
                other_positions_maint_margin=other_positions_maint_margin,
                other_positions_unrealised_pnl=other_positions_unrealised_pnl,
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
