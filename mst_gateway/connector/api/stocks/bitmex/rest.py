import json
import httpx
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional, Union, Tuple
from mst_gateway.storage import StateStorageKey
from mst_gateway.calculator import BitmexFinFactory
from mst_gateway.connector.api.types import OrderSchema, ExchangeDrivers
from mst_gateway.connector.api.utils.rest import validate_exchange_order_id
from mst_gateway.connector.api.stocks.bitmex.lib import BitmexApiClient
from mst_gateway.connector.api.stocks.bitmex.lib.exceptions import BitmexAPIException
from . import utils, var
from .utils import binsize2timedelta
from ...rest import StockRestApi
from .... import api
from .....exceptions import ConnectorError, RecoverableError, NotFoundError
from .....utils import j_dumps
from ...rest.throttle import ThrottleRest


class BitmexRestApi(StockRestApi):
    driver = ExchangeDrivers.bitmex
    name = 'bitmex'
    fin_factory = BitmexFinFactory()
    throttle = ThrottleRest(rest_limit=var.BITMEX_THROTTLE_LIMITS.get('rest'),
                            order_limit=var.BITMEX_THROTTLE_LIMITS.get('order'))

    def _connect(self, **kwargs):
        self._keepalive = bool(kwargs.get('keepalive', False))
        self._compress = bool(kwargs.get('compress', False))

        return BitmexApiClient(api_key=self.auth.get('api_key'),
                               api_secret=self.auth.get('api_secret'),
                               testnet=self.test)

    def ping(self, schema: str) -> bool:
        try:
            self._bitmex_api(self._handler.get_instrument, symbol=utils.symbol2stock('xbtusd'))
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
        quote_bins = self._bitmex_api(self._handler.get_trade_bucketed,
                                      symbol=utils.symbol2stock(symbol),
                                      binSize=binsize,
                                      reverse=True,
                                      partial=True,
                                      start=offset,
                                      count=count,
                                      **self._api_kwargs(kwargs))
        return [utils.load_quote_bin_data(data, state_data, binsize=binsize) for data in quote_bins]

    def list_quote_bins(self, symbol, schema, binsize='1m', count=100, **kwargs) -> list:
        kwargs['state_data'] = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(),
                                                                                                      {})
        pages = count // var.BITMEX_MAX_QUOTE_BINS_COUNT + 1
        pages_mod = count % var.BITMEX_MAX_QUOTE_BINS_COUNT or var.BITMEX_MAX_QUOTE_BINS_COUNT
        quote_bins = []
        for i in range(pages):
            if i == pages - 1:
                items_count = pages_mod
            else:
                items_count = var.BITMEX_MAX_QUOTE_BINS_COUNT
            quotes = self._list_quote_bins_page(symbol=symbol,
                                                schema=schema,
                                                binsize=binsize,
                                                offset=i * var.BITMEX_MAX_QUOTE_BINS_COUNT,
                                                count=items_count,
                                                **kwargs)
            quotes_len = len(quotes)
            if quotes_len == 1 and quotes_len != items_count:
                break
            quote_bins += quotes
        return list(reversed(quote_bins))

    def get_user(self, **kwargs) -> dict:
        data = self._bitmex_api(self._handler.get_user, **kwargs)
        return utils.load_user_data(data)

    def get_api_key_permissions(self, schemas: list, **kwargs) -> Tuple[dict, Optional[int]]:
        auth_expired = None
        default_schemas = [
            OrderSchema.margin,
        ]
        permissions = {schema: False for schema in schemas if schema in default_schemas}
        try:
            all_api_keys = self._bitmex_api(self._handler.get_api_keys)
        except ConnectorError:
            return permissions, auth_expired
        return utils.load_api_key_permissions(all_api_keys, self.auth.get('api_key'), permissions.keys()), auth_expired

    def get_wallet(self, **kwargs) -> dict:
        schema = kwargs.pop('schema', OrderSchema.margin).lower()
        if schema == OrderSchema.margin:
            data = self._bitmex_api(self._handler.get_user_margin, **kwargs)
            return utils.load_wallet_data(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_wallet_detail(self, schema: str, asset: str, **kwargs) -> dict:
        if schema == OrderSchema.margin:
            data = self._bitmex_api(self._handler.get_user_margin, **kwargs)
            return utils.load_wallet_detail_data(data, asset)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_wallet_extra_data(self, schema: str, **kwargs) -> dict:
        return {}

    def get_wallet_detail_extra_data(self, schema: str, asset: str, **kwargs) -> dict:
        return {}

    def get_assets_balance(self, schema: str, **kwargs) -> dict:
        if schema == OrderSchema.margin:
            data = self._bitmex_api(self._handler.get_user_margin, **kwargs)
            return utils.load_wallet_asset_balance(data)
        raise ConnectorError(f"Invalid schema {schema}.")

    def wallet_transfer(self, from_wallet: str, to_wallet: str, asset: str, amount: float, symbol: str = None):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def wallet_borrow(self, schema: str, asset: str, amount: float, **kwargs):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def wallet_repay(self, schema: str, asset: str, amount: float, **kwargs):
        raise ConnectorError('Bitmex api error. Details: Invalid method.')

    def get_symbol(self, symbol, schema) -> dict:
        instruments = self._bitmex_api(self._handler.get_instrument, symbol=utils.symbol2stock(symbol))
        if not instruments:
            return dict()
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{OrderSchema.margin}".lower()
        ).get(utils.stock2symbol(symbol), dict())
        return utils.load_symbol_data(instruments[0], state_data)

    def list_symbols(self, schema, **kwargs) -> list:
        data = self._bitmex_api(self._handler.get_instrument_active, **kwargs)
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{schema}"
        )
        symbols = []
        for d in data:
            symbol_state = state_data.get(utils.stock2symbol(d.get('symbol')))
            if symbol_state:
                symbols.append(utils.load_symbol_data(d, symbol_state))
        return symbols

    def get_exchange_symbol_info(self, schema: str) -> list:
        if schema == OrderSchema.margin:
            data = self._bitmex_api(self._handler.get_instrument_active)
            assets_config = self._bitmex_api(self._handler.get_wallet_assets)
            return utils.load_exchange_symbol_info(data, assets_config)
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
        data = self._bitmex_api(self._handler.create_order, **params)
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{OrderSchema.margin}"
        ).get(symbol.lower(), dict())
        return utils.load_order_data(schema, data, state_data)

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
        data = self._bitmex_api(self._handler.cancel_all_orders)
        return bool(data)

    def cancel_order(self, exchange_order_id: str, symbol: str, schema: str) -> dict:
        validate_exchange_order_id(exchange_order_id)
        params = dict(exchange_order_id=exchange_order_id)
        params = utils.map_api_parameter_names(params)

        data = self._bitmex_api(self._handler.cancel_order, **params)
        if isinstance(data[0], dict) and data[0].get('error'):
            error = data[0].get('error')
            status = data[0].get('ordStatus')
            if status in ('Filled', 'Canceled', None):
                raise NotFoundError(error)
            raise ConnectorError(error)
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{OrderSchema.margin}"
        ).get(data[0]['symbol'].lower(), dict())
        return utils.load_order_data(schema, data[0], state_data)

    def get_order(self, exchange_order_id: str, symbol: str,
                  schema: str) -> Optional[dict]:
        params = dict(exchange_order_id=exchange_order_id)
        params = utils.map_api_parameter_names(params)
        data = self._bitmex_api(self._handler.get_orders, reverse=True, filter=j_dumps(params))
        if not data:
            return None
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{OrderSchema.margin}"
        ).get(data[0]['symbol'].lower(), dict())
        return utils.load_order_data(schema, data[0], state_data)

    def list_orders(self, schema: str, symbol: str = None, active_only: bool = True,
                    count: int = None, offset: int = 0) -> list:
        state_data = {}
        options = {'filter': {}}
        if symbol:
            options['filter']['symbol'] = symbol
            state_data = self.storage.get(
                f"{StateStorageKey.symbol}.{self.name}.{OrderSchema.margin}"
            ).get(symbol.lower(), dict())
        if active_only:
            options['filter']['open'] = True
        if count:
            options['count'] = count
        if offset > 0:
            options['start'] = offset
        options['filter'] = j_dumps(options['filter'])
        orders = self._bitmex_api(self._handler.get_orders, reverse=True, **options)
        return [utils.load_order_data(schema, data, state_data) for data in orders]

    def list_trades(self, symbol: str, schema: str, **kwargs) -> list:
        trades = self._bitmex_api(self._handler.get_trade,
                                  symbol=utils.symbol2stock(symbol),
                                  reverse=True,
                                  **self._api_kwargs(kwargs))
        state_data = self.storage.get(
            f"{StateStorageKey.symbol}.{self.name}.{schema}"
        ).get(symbol.lower(), dict())
        return [utils.load_trade_data(data, state_data) for data in trades]

    def close_order(self, exchange_order_id: str, symbol: str, schema: str) -> bool:
        order = self.get_order(exchange_order_id, symbol, schema)
        return self.close_all_orders(order['symbol'], schema)

    def close_all_orders(self, symbol: str, schema: str) -> bool:
        data = self._bitmex_api(self._handler.close_position, symbol=utils.symbol2stock(symbol))
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
        ob_items = self._bitmex_api(
            self._handler.get_order_book_l2,
            symbol=utils.symbol2stock(symbol),
            depth=_depth,
        )
        state_data = self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}").get(symbol.lower(), dict())
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
            instruments = self._bitmex_api(self._handler.get_instrument, symbol=utils.symbol2stock(symbol), **kwargs)
        else:
            instruments = self._bitmex_api(self._handler.get_instrument_active, **kwargs)
        return utils.load_currency_exchange_symbol(instruments)

    def get_symbols_currencies(self, schema: str) -> dict:
        instruments = self._bitmex_api(self._handler.get_instrument_active)
        return utils.load_symbols_currencies(instruments,
                                             self.storage.get(f"{StateStorageKey.symbol}.{self.name}.{schema}"))

    def list_order_commissions(self, schema: str) -> list:
        if schema == OrderSchema.margin:
            commissions = self._bitmex_api(self._handler.get_user_commission)
            return utils.load_commissions(commissions)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_vip_level(self, schema: str) -> str:
        if schema == OrderSchema.margin:
            try:
                trading_volume = self._bitmex_api(self._handler.get_user_trading_volume)
                trading_volume = trading_volume[0].get('advUsd')
            except (IndexError, AttributeError):
                trading_volume = 0
            return utils.load_vip_level(trading_volume)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_funding_rates(self, symbol: str, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        if schema.lower() == OrderSchema.margin:
            funding_rates = self._bitmex_api(
                method=self._handler.get_funding,
                symbol=utils.symbol2stock(symbol),
                startTime=datetime.now() - timedelta(hours=period_hour * period_multiplier, minutes=1),
                count=500,
            )
            return utils.load_funding_rates(funding_rates)
        raise ConnectorError(f"Invalid schema {schema}.")

    def list_funding_rates(self, schema: str, period_multiplier: int, period_hour: int = 8) -> list:
        if schema == OrderSchema.margin:
            funding_rates = self._bitmex_api(
                method=self._handler.get_funding,
                startTime=datetime.now() - timedelta(hours=period_hour * period_multiplier, minutes=1),
                count=500,
            )
            return utils.load_funding_rates(funding_rates)
        raise ConnectorError(f"Invalid schema {schema}.")

    def get_leverage(self, schema: str, symbol: str, **kwargs) -> tuple:
        if schema != OrderSchema.margin:
            raise ConnectorError(f"Invalid schema {schema}.")
        response = self._bitmex_api(
            self._handler.get_position, filter=j_dumps({'symbol': utils.symbol2stock(symbol)})
        )
        if response:
            return utils.load_leverage(response[0])
        response = self._bitmex_api(self._handler.get_instrument, symbol=utils.symbol2stock(symbol))
        _data = response[0] if response else {'initMargin': 0}
        _tmp = {
            'crossMargin': False,
            'leverage': None if _data.get('initMargin', 0) <= 0 else 1 / _data['initMargin']
        }
        return utils.load_leverage(_tmp)

    def change_leverage(self, schema: str, symbol: str, leverage_type: str,
                        leverage: Union[float, int], **kwargs) -> tuple:
        if schema != OrderSchema.margin:
            raise ConnectorError(f"Invalid schema {schema}.")
        response = self._bitmex_api(
            self._handler.update_position_leverage, symbol=utils.symbol2stock(symbol),
            leverage=utils.store_leverage(leverage_type, leverage)
        )
        return utils.load_leverage(response)

    def get_position(self, schema: str, symbol: str, **kwargs) -> dict:
        if schema != OrderSchema.margin:
            raise ConnectorError(f"Invalid schema {schema}.")
        response = self._bitmex_api(
            self._handler.get_position, **{'filter': j_dumps({'symbol': symbol.upper()})}
        )
        try:
            response = response[0]
            if utils.to_float(response.get('currentQty')):
                return utils.load_position(response, schema)
        except IndexError:
            pass
        return {}

    def list_positions(self, schema: str, **kwargs) -> list:
        if schema != OrderSchema.margin:
            raise ConnectorError(f"Invalid schema {schema}.")
        response = self._bitmex_api(self._handler.get_position, **kwargs)
        return utils.load_positions_list(response, schema)

    def get_positions_state(self, schema: str) -> dict:
        if schema != OrderSchema.margin:
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
            **kwargs,
    ) -> dict:
        schema = schema.lower()
        if schema != OrderSchema.margin:
            raise ConnectorError(f'Invalid schema {schema}.')
        return {
            'liquidation_price': self.fin_factory.calc_liquidation_price(
                side=side,
                leverage_type=leverage_type,
                entry_price=price,
                maint_margin=kwargs.get('wallet_detail', {}).get('maint_margin'),
                volume=volume,
                wallet_balance=wallet_balance,
                taker_fee=kwargs.get('taker_fee'),
                funding_rate=kwargs.get('funding_rate'),
                leverage=kwargs.get('leverage'),
            )}

    def _bitmex_api(self, method: callable, **kwargs):
        rest_method, url = self.handler.get_method_info(method.__name__, **kwargs)
        if not rest_method:
            raise ConnectorError("Bitmex request method error.")
        if not self.ratelimit:
            self.validate_throttling(self.throttle_hash_name())
        else:
            proxies = self.ratelimit.get_proxies(
                method=rest_method, url=str(url), hashed_uid=self._generate_hashed_uid()
            )
            if not proxies:
                raise ConnectorError('Ratelimit service error.')
            kwargs['proxies'] = proxies
        headers = {}
        if self._keepalive:
            headers['Connection'] = "keep-alive"
        if self._compress:
            headers['Accept-Encoding'] = "deflate, gzip;q=1.0, *;q=0.5"
        kwargs['headers'] = headers
        try:
            resp = method(**kwargs)
            data = self.handler.handle_response(resp)
            if not self.ratelimit:
                self.throttle.set(
                    key=self.throttle_hash_name(),
                    limit=(int(resp.headers.get('X-RateLimit-Limit', 0)) -
                           int(resp.headers.get('X-RateLimit-Remaining', 0))),
                    reset=int(resp.headers.get('X-RateLimit-Reset', 0)),
                    scope='rest'
                )
            return data
        except BitmexAPIException as exc:
            if not self.ratelimit:
                self.throttle.set(
                    key=self.throttle_hash_name(),
                    **self.__get_limit_headers(exc.response.headers)
                )
            message = f"Bitmex api error. Details: {exc.status_code}, {exc.message}"
            if exc.status_code == 429 or exc.status_code >= 500:
                raise RecoverableError(message)
            elif exc.status_code == 403:
                self.logger.critical(f"{self.__class__.__name__}: {exc}")
            elif exc.status_code == 404:
                raise NotFoundError(message)
            raise ConnectorError(message)
        except Exception as exc:
            self.logger.error(f"Bitmex api error. Details: {exc}")
            raise ConnectorError("Bitmex api error.")

    def _generate_hashed_uid(self):
        return sha256(self.auth.get('api_key', '').encode('utf-8')).hexdigest()

    def __get_limit_headers(self, headers: httpx.Headers):
        limit_header = {
            'limit': 0,
            'reset': None,
            'scope': 'rest',
        }
        if h := headers.get('retry-after'):
            try:
                retry_after = int(h)
                limit_header.update({
                    'limit': float('inf'),
                    'reset': self.__parse_reset(retry_after),
                    'timeout': retry_after
                })
            except (ValueError, TypeError):
                pass
        return limit_header

    def __parse_reset(self, retry_after: Optional[int]) -> int:
        return int((datetime.utcnow() + timedelta(seconds=retry_after or 60)).timestamp())
