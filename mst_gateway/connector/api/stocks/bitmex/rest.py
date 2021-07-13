import json
from datetime import datetime, timedelta
from typing import Optional, Union
from bravado.exception import HTTPError
from .lib import (
    bitmex_connector, APIKeyAuthenticator, SwaggerClient
)
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector.api.types import LeverageType, OrderSchema
from mst_gateway.connector.api.utils.rest import validate_exchange_order_id
from . import utils, var
from .utils import binsize2timedelta
from ...rest import StockRestApi
from .... import api
from .....exceptions import ConnectorError, RecoverableError, NotFoundError
from .....utils import j_dumps


class BitmexFactory:
    BASE_URL = "https://www.bitmex.com/api/v1"
    TEST_URL = "https://testnet.bitmex.com/api/v1"
    BITMEX_SWAGGER = None   # type: SwaggerClient
    TBITMEX_SWAGGER = None  # type: SwaggerClient

    @classmethod
    def make_client(cls, test):
        if test:
            if not cls.TBITMEX_SWAGGER:
                cls.TBITMEX_SWAGGER = bitmex_connector(test=test)
            return cls.TBITMEX_SWAGGER
        else:
            if not cls.BITMEX_SWAGGER:
                cls.BITMEX_SWAGGER = bitmex_connector(test=test)
            return cls.BITMEX_SWAGGER


class BitmexRestApi(StockRestApi):
    name = 'bitmex'
    fin_factory = BitmexFinFactory()

    def _connect(self, **kwargs):
        self._keepalive = bool(kwargs.get('keepalive', False))
        self._compress = bool(kwargs.get('compress', False))
        return BitmexFactory.make_client(test=self.test)

    @property
    def _authenticator(self):
        self._auth = self._auth if isinstance(self._auth, dict) else {}
        return APIKeyAuthenticator(
            host=BitmexFactory.TEST_URL if self.test else BitmexFactory.BASE_URL,
            api_key=self._auth.get('api_key'),
            api_secret=self._auth.get('api_secret')
        )

    def ping(self, schema: str) -> bool:
        try:
            self._bitmex_api(self._handler.Instrument.Instrument_get, symbol=utils.symbol2stock('xbtusd'))
        except ConnectorError:
            return False
        return True

    def _api_kwargs(self, kwargs):
        # pylint: disable=no-self-use
        api_kwargs = dict(filter={})
        for _k, _v in kwargs.items():
            if _k == 'date_from':
                api_kwargs['startTime'] = _v
            if _k == 'date_to':
                api_kwargs['endTime'] = _v
            if _k == 'count':
                api_kwargs['count'] = _v
        if not api_kwargs['filter']:
            del api_kwargs['filter']
        else:
            api_kwargs['filter'] = json.dumps(api_kwargs['filter'])
        return api_kwargs

    def _list_quote_bins_page(self, symbol, schema, binsize='1m', count=100, offset=0,
                              **kwargs):
        state_data = kwargs.pop('state_data', dict())
        if 'date_to' in kwargs:
            kwargs['date_to'] += binsize2timedelta(binsize)
        if 'date_from' in kwargs:
            kwargs['date_from'] += binsize2timedelta(binsize)
        quote_bins, _ = self._bitmex_api(self._handler.Trade.Trade_getBucketed,
                                         symbol=utils.symbol2stock(symbol),
                                         binSize=binsize,
                                         reverse=True,
                                         partial=True,
                                         start=offset,
                                         count=count,
                                         **self._api_kwargs(kwargs))
        return [utils.load_quote_bin_data(data, state_data, binsize=binsize) for data in quote_bins]

    def list_quote_bins(self, symbol, schema, binsize='1m', count=100, **kwargs) -> list:
        kwargs['state_data'] = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
        pages = int((count - 1) / var.BITMEX_MAX_QUOTE_BINS_COUNT) + 1
        rest = count % var.BITMEX_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        for i in range(pages):
            if i == pages - 1:
                items_count = rest
            else:
                items_count = var.BITMEX_MAX_QUOTE_BINS_COUNT
            quotes = self._list_quote_bins_page(symbol=symbol,
                                                schema=schema,
                                                binsize=binsize,
                                                offset=i * var.BITMEX_MAX_QUOTE_BINS_COUNT,
                                                count=items_count,
                                                **kwargs)
            quote_bins += quotes
        return list(reversed(quote_bins))

    def get_user(self, **kwargs) -> dict:
        data, _ = self._bitmex_api(self._handler.User.User_get, **kwargs)
        return utils.load_user_data(data)

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', OrderSchema.margin1).lower()
        if schema == OrderSchema.margin1:
            data, _ = self._bitmex_api(self._handler.User.User_getMargin, **kwargs)
            currencies = self.storage.get('currency', self.name, schema)
            assets = kwargs.get('assets', ('btc', 'usd'))
            fields = ('balance', 'unrealised_pnl', 'margin_balance')
            return utils.load_wallet_data(data, currencies, assets, fields)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        if schema == OrderSchema.margin1:
            data, _ = self._bitmex_api(self._handler.User.User_getMargin, **kwargs)
            return {
                OrderSchema.margin1: utils.load_wallet_detail_data(data, asset)
            }
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_cross_collaterals(self, schema: str, **kwargs) -> list:
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        if schema == OrderSchema.margin1:
            data, _ = self._bitmex_api(self._handler.User.User_getMargin, **kwargs)
            return utils.load_wallet_asset_balance(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def wallet_borrow(self, schema: str, asset: str, amount: float, **kwargs):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def wallet_repay(self, schema: str, asset: str, amount: float, **kwargs):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def get_symbol(self, symbol, schema) -> dict:
        instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_get,
                                          symbol=utils.symbol2stock(symbol))
        if not instruments:
            return dict()
        state_data = self.storage.get(
            'symbol', self.name, OrderSchema.margin1
        ).get(utils.stock2symbol(symbol), dict())
        return utils.load_symbol_data(instruments[0], state_data)

    def list_symbols(self, schema, **kwargs) -> list:
        data, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive,
                                   **kwargs)
        state_data = self.storage.get(
            'symbol', self.name, OrderSchema.margin1
        )
        symbols = []
        for d in data:
            symbol_state = state_data.get(utils.stock2symbol(d.get('symbol')))
            if symbol_state:
                symbols.append(utils.load_symbol_data(d, symbol_state))
        return symbols

    def get_exchange_symbol_info(self, schema: str) -> list:
        if schema == OrderSchema.margin1:
            data, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive)
            return utils.load_exchange_symbol_info(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def create_order(self, symbol: str, schema: str, side: int, volume: float,
                     order_type: str = api.OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        params = dict(
            symbol=utils.symbol2stock(symbol),
            order_type=order_type,
            side=utils.store_order_side(side),
            volume=volume,
            price=price
        )
        params = utils.generate_parameters_by_order_type(params, options)

        data, _ = self._bitmex_api(self._handler.Order.Order_new, **params)
        state_data = self.storage.get(
            'symbol', self.name, OrderSchema.margin1
        ).get(symbol.lower(), dict())
        return utils.load_order_data(data, state_data)

    def update_order(self, exchange_order_id: str, symbol: str,
                     schema: str, side: int, volume: float,
                     order_type: str = api.OrderType.market,
                     price: float = None, options: dict = None) -> dict:
        """
        Updates an order by deleting an existing order and creating a new one.

        """
        self.cancel_order(exchange_order_id, symbol, schema)
        return self.create_order(symbol, schema, side, volume,
                                 order_type, price, options=options)

    def cancel_all_orders(self, schema: str):
        data, _ = self._bitmex_api(self._handler.Order.Order_cancelAll)
        return bool(data)

    def cancel_order(self, exchange_order_id: str, symbol: str, schema: str) -> dict:
        validate_exchange_order_id(exchange_order_id)
        params = dict(exchange_order_id=exchange_order_id)
        params = utils.map_api_parameter_names(params)

        data, _ = self._bitmex_api(self._handler.Order.Order_cancel, **params)
        if isinstance(data[0], dict) and data[0].get('error'):
            error = data[0].get('error')
            status = data[0].get('ordStatus')
            if status in ('Filled', 'Canceled'):
                raise NotFoundError(error)
            raise ConnectorError(error)
        return data

    def get_order(self, exchange_order_id: str, symbol: str,
                  schema: str) -> Optional[dict]:
        params = dict(exchange_order_id=exchange_order_id)
        params = utils.map_api_parameter_names(params)
        data, _ = self._bitmex_api(self._handler.Order.Order_getOrders,
                                   reverse=True,
                                   filter=j_dumps(params))
        if not data:
            return None
        state_data = self.storage.get(
            'symbol', self.name, OrderSchema.margin1
        ).get(data[0]['symbol'].lower(), dict())
        return utils.load_order_data(data[0], state_data)

    def list_orders(self,
                    schema: str,
                    symbol: str,
                    active_only: bool = True,
                    count: int = None,
                    offset: int = 0,
                    options: dict = None) -> list:
        if options is None:
            options = {}
        if active_only:
            if 'filter' not in options:
                options['filter'] = {}
            options['filter']['open'] = True
            options['filter'] = j_dumps(options['filter'])
        if count is not None:
            options['count'] = count
        if offset > 0:
            options['start'] = offset
        orders, _ = self._bitmex_api(self._handler.Order.Order_getOrders,
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     **options)
        state_data = self.storage.get(
            'symbol', self.name, OrderSchema.margin1
        ).get(symbol.lower(), dict())
        return [utils.load_order_data(data, state_data) for data in orders]

    def list_trades(self, symbol: str, schema: str, **kwargs) -> list:
        trades, _ = self._bitmex_api(self._handler.Trade.Trade_get,
                                     symbol=utils.symbol2stock(symbol),
                                     reverse=True,
                                     **self._api_kwargs(kwargs))
        state_data = self.storage.get(
            'symbol', self.name, schema
        ).get(symbol.lower(), dict())
        return [utils.load_trade_data(data, state_data) for data in trades]

    def close_order(self, exchange_order_id: str, symbol: str, schema: str) -> bool:
        order = self.get_order(exchange_order_id, symbol, schema)
        return self.close_all_orders(order['symbol'], schema)

    def close_all_orders(self, symbol: str, schema: str) -> bool:
        data, _ = self._bitmex_api(self._handler.Order.Order_closePosition,
                                   symbol=utils.symbol2stock(symbol))
        return bool(data)

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
        ob_depth = depth or 0
        if ob_depth:
            ob_depth += offset
        _depth = ob_depth if min_volume_buy is None and min_volume_sell is None else 0
        ob_items, _ = self._bitmex_api(
            self._handler.OrderBook.OrderBook_getL2, symbol=utils.symbol2stock(symbol),
            depth=_depth,
        )
        state_data = self.storage.get('symbol', self.name, schema).get(symbol.lower(), dict())
        splitted_ob = utils.split_order_book(ob_items, state_data)
        filtered_ob = utils.filter_order_book(splitted_ob, min_volume_buy, min_volume_sell)
        data_ob = utils.slice_order_book(filtered_ob, depth, offset)
        if side is not None and split:
            return {side: data_ob[side]}
        elif side is not None:
            return data_ob[side]
        elif split:
            return data_ob
        return data_ob[api.SELL] + data_ob[api.BUY]

    def currency_exchange_symbols(self, schema: str, symbol: str = None, **kwargs) -> list:
        if symbol:
            instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_get,
                                              symbol=utils.symbol2stock(symbol),
                                              **kwargs)
        else:
            instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive,
                                              **kwargs)
        return utils.load_currency_exchange_symbol(instruments)

    def get_symbols_currencies(self, schema: str) -> dict:
        instruments, _ = self._bitmex_api(self._handler.Instrument.Instrument_getActive)
        return utils.load_symbols_currencies(instruments)

    def get_wallet_summary(self, schemas: iter, **kwargs) -> dict:
        if not schemas:
            schemas = (OrderSchema.margin1,)
        assets = kwargs.get('assets', ('btc', 'usd'))
        fields = ('balance', 'unrealised_pnl', 'margin_balance')

        total_summary = dict()
        for schema in schemas:
            total_balance = {schema: {}}
            if schema == OrderSchema.margin1:
                balances = self.get_wallet(schema=schema)['balances']
                currencies = self.storage.get('currency', self.name, OrderSchema.margin1)
            else:
                continue
            for asset in assets:
                total_balance[schema][asset] = utils.load_wallet_summary(currencies, balances, asset, fields)
            utils.load_total_wallet_summary(total_summary, total_balance, assets, fields)
        return total_summary

    def list_order_commissions(self, schema: str) -> list:
        if schema == OrderSchema.margin1:
            commissions, _ = self._bitmex_api(self._handler.User.User_getCommission)
            return utils.load_commissions(commissions)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_vip_level(self, schema: str) -> str:
        return '0'

    def get_funding_rates(self, symbol: str, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        if schema.lower() == OrderSchema.margin1:
            funding_rates, _ = self._bitmex_api(
                symbol=utils.symbol2stock(symbol),
                method=self._handler.Funding.Funding_get,
                startTime=datetime.now() - timedelta(hours=period_hour*period_multiplier, minutes=1),
                count=500,
            )
            return utils.load_funding_rates(funding_rates)
        raise ConnectorError(f"Invalid schema {schema}.")

    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        if schema == OrderSchema.margin1:
            funding_rates, _ = self._bitmex_api(
                method=self._handler.Funding.Funding_get,
                startTime=datetime.now() - timedelta(hours=period_hour*period_multiplier, minutes=1),
                count=500,
            )
            return utils.load_funding_rates(funding_rates)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f"Invalid schema {schema}.")
        response, _ = self._bitmex_api(
            self._handler.Position.Position_get, filter=j_dumps({'symbol': utils.symbol2stock(symbol)})
        )
        if response:
            return utils.load_leverage(response[0])
        response, _ = self._bitmex_api(self._handler.Instrument.Instrument_get, symbol=utils.symbol2stock(symbol))
        _data = response[0] if response else {'initMargin': 0}
        _tmp = {
            'crossMargin': False,
            'leverage': None if _data.get('initMargin', 0) <= 0 else 1 / _data['initMargin']
        }
        return utils.load_leverage(_tmp)

    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f"Invalid schema {schema}.")
        response, _ = self._bitmex_api(
            self._handler.Position.Position_updateLeverage, symbol=utils.symbol2stock(symbol),
            leverage=utils.store_leverage(leverage_type, leverage)
        )
        return utils.load_leverage(response)

    def get_position(self, schema: str, symbol: str, **kwargs) -> dict:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f"Invalid schema {schema}.")
        response, _ = self._bitmex_api(
            self._handler.Position.Position_get, **{'filter': j_dumps({'symbol': symbol.upper()})}
        )
        try:
            response = response[0]
            if utils.to_float(response.get('currentQty')):
                return utils.load_position(response, schema)
        except IndexError:
            pass
        return {}

    def list_positions(self, schema: str, **kwargs) -> list:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f"Invalid schema {schema}.")
        response, _ = self._bitmex_api(
            self._handler.Position.Position_get
        )
        return utils.load_positions_list(response, schema)

    def get_positions_state(self, schema: str) -> dict:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f"Invalid schema {schema}.")
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
        leverage: Optional[float],
        mark_price: Optional[float],
        **kwargs,
    ) -> dict:
        if schema != OrderSchema.margin1:
            raise ConnectorError(f'Invalid schema {schema}.')
        maint_margin = kwargs.get('wallet_detail',  {}).get(schema, {}).get('maint_margin')
        params = {
            'taker_fee': kwargs.get('taker_fee'),
            'funding_rate': kwargs.get('funding_rate'),
        }
        if leverage_type == LeverageType.isolated:
            params.update({
                'leverage': leverage,
            })
            liquidation_price = self.fin_factory.calc_liquidation_isolated_price(
                entry_price=price, maint_margin=maint_margin, side=side, **params,
            )
        else:
            params.update({
                'quantity': volume,
                'margin_balance': wallet_balance,
            })
            liquidation_price = self.fin_factory.calc_liquidation_cross_price(
                entry_price=price, maint_margin=maint_margin, side=side, **params,
            )
        return {'liquidation_price': liquidation_price}

    def _bitmex_api(self, method: callable, **kwargs):
        headers = {}
        if self._keepalive:
            headers['Connection'] = "keep-alive"
        if self._compress:
            headers['Accept-Encoding'] = "deflate, gzip;q=1.0, *;q=0.5"
        try:
            resp = method(
                authenticator=self._authenticator,
                _request_options={'headers': headers},
                **kwargs
            ).response()

            self.throttle.set(
                key=self._throttle_hash_name,
                limit=(int(resp.incoming_response.headers.get('X-RateLimit-Limit', 0)) -
                       int(resp.incoming_response.headers.get('X-RateLimit-Remaining', 0))),
                reset=int(resp.incoming_response.headers.get('X-RateLimit-Reset', 0)),
                scope='rest'
            )

            return resp.result, resp.metadata
        except HTTPError as exc:
            message = exc.message
            if not message and isinstance(exc.swagger_result, dict):
                message = exc.swagger_result.get('error', {}).get('message')
            full_message = f"Bitmex api error. Details: {exc.status_code}, {message}"
            if int(exc.status_code) == 429 or int(exc.status_code) >= 500:
                raise RecoverableError(full_message)
            elif int(exc.status_code) == 404:
                raise NotFoundError(full_message)
            raise ConnectorError(full_message)
