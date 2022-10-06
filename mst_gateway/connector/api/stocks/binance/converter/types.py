from copy import deepcopy
from typing import Optional
from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema
)
from mst_gateway.exceptions import ConnectorError


class BinanceOrderTypeConverter(BaseOrderTypeConverter):
    """
    Order type converter for Binance

    """
    CREATE_PARAMETER_NAMES_MAP = {
        'order_id': 'newClientOrderId',
    }

    BASE_PARAMETER_NAMES_MAP = {
        'order_id': 'origClientOrderId',
        'exchange_order_id': 'orderId',
        'order_type': 'type',
        'volume': 'quantity',
        'iceberg_volume': 'icebergQty',
        'stop_price': 'stopPrice',
        'reduce_only': 'reduceOnly',
        'new_order_resp_type': 'newOrderRespType',
        'position_side': 'positionSide',
        'ttl': 'timeInForce',
        'H1': 'GTC',
        'H4': 'GTC',
        'D1': 'GTC',
        'GTC': 'GTC',
        'FOK': 'FOK',
        'IOC': 'IOC',
        'GTX': 'GTX'
    }

    SPOT_PARAMETER_NAMES_MAP = {
        **BASE_PARAMETER_NAMES_MAP,
        'step': 'trailingDelta',
    }

    FUTURES_PARAMETER_NAMES_MAP = {
        **BASE_PARAMETER_NAMES_MAP,
        'step': 'callbackRate'
    }

    DEFAULT_PARAMETERS = [
        'newClientOrderId',
        'newOrderRespType',
        'symbol',
        'type',
        'side',
        'quantity',
        'quoteOrderQty'
    ]

    PARAMETERS_BY_ORDER_TYPE_MAP = {
        OrderSchema.exchange: {
            'MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS
                ],
                'additional_params': {}
            },
            'LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'icebergQty',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP_LOSS_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP_LOSS': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'quantity'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'timeInForce',
                    'stopPrice',
                    'price',
                    'quantity'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                ],
                'additional_params': {}
            },
            'TRAILING_STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'trailingDelta',
                    'reduceOnly'
                ],
                'additional_params': {
                    'type': 'STOP_LOSS'
                }
            }
        },
        OrderSchema.margin_cross: {
            'MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'isIsolated',
                    'sideEffectType'
                ],
                'additional_params': {}
            },
            'LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'isIsolated',
                    'sideEffectType'
                    'icebergQty',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP_LOSS_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'trailingDelta',
                    'timeInForce',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'STOP_LOSS': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'quantity',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'timeInForce',
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TRAILING_STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'trailingDelta',
                    'reduceOnly'
                ],
                'additional_params': {
                    'type': 'STOP_LOSS'
                }
            }
        },
        OrderSchema.margin_isolated: {
            'MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'isIsolated',
                    'sideEffectType'
                ],
                'additional_params': {}
            },
            'LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'isIsolated',
                    'sideEffectType'
                    'icebergQty',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP_LOSS_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'trailingDelta',
                    'timeInForce',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'STOP_LOSS': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'quantity',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT_LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'timeInForce',
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TRAILING_STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'trailingDelta',
                    'reduceOnly'
                ],
                'additional_params': {
                    'type': 'STOP_LOSS'
                }
            }
        },
        OrderSchema.margin: {
            'MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'reduceOnly',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'stopPrice',
                    'quantity',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly',
                    'positionSide'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'quantity',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TRAILING_STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'callbackRate',
                    'stopPrice',
                    'activationPrice',
                    'reduceOnly'
                ],
                'additional_params': {
                    'callbackRate': 1
                }
            }
        },
        OrderSchema.margin_coin: {
            'MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'LIMIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'reduceOnly',
                    'timeInForce',
                    'price'
                ],
                'additional_params': {}
            },
            'STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly',
                    'positionSide'
                ],
                'additional_params': {}
            },
            'STOP': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'positionSide',
                    'stopPrice',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'price',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TAKE_PROFIT_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'stopPrice',
                    'reduceOnly'
                ],
                'additional_params': {}
            },
            'TRAILING_STOP_MARKET': {
                'params': [
                    *DEFAULT_PARAMETERS,
                    'activationPrice',
                    'stopPrice',
                    'callbackRate',
                    'reduceOnly'
                ],
                'additional_params': {
                    'callbackRate': 1
                }
            }
        }
    }

    LOAD_TYPE_MAP = {
        OrderSchema.margin_cross: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            # 'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            # 'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with LONG type value
            # 'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin_isolated: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            # 'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            # 'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with LONG type value
            # 'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.exchange: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP_LOSS_LIMIT': OrderType.stop_limit,
            # 'STOP_LOSS': OrderType.stop_market,
            'TAKE_PROFIT_LIMIT': OrderType.take_profit_limit,
            # 'TAKE_PROFIT': OrderType.take_profit_market,
            # used if exchange order data contain a trailingDelta field with number type value
            # 'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP': OrderType.stop_limit,
            'STOP_MARKET': OrderType.stop_market,
            'TAKE_PROFIT': OrderType.take_profit_limit,
            'TAKE_PROFIT_MARKET': OrderType.take_profit_market,
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        },
        OrderSchema.margin_coin: {
            'LIMIT': OrderType.limit,
            'MARKET': OrderType.market,
            'STOP': OrderType.stop_limit,
            'STOP_MARKET': OrderType.stop_market,
            'TAKE_PROFIT': OrderType.take_profit_limit,
            'TAKE_PROFIT_MARKET': OrderType.take_profit_market,
            'TRAILING_STOP_MARKET': OrderType.trailing_stop,
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin_cross: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            # OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            # OrderType.trailing_stop: 'TRAILING_STOP_MARKET',
        },
        OrderSchema.margin_isolated: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            # OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            # OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        },
        OrderSchema.exchange: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP_LOSS_LIMIT',
            OrderType.stop_market: 'MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT_LIMIT',
            # OrderType.take_profit_market: 'TAKE_PROFIT',
            # OrderType.trailing_stop: 'TRAILING_STOP_MARKET',
        },
        OrderSchema.margin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        },
        OrderSchema.margin_coin: {
            OrderType.limit: 'LIMIT',
            OrderType.market: 'MARKET',
            OrderType.stop_limit: 'STOP',
            OrderType.stop_market: 'STOP_MARKET',
            OrderType.take_profit_limit: 'TAKE_PROFIT',
            OrderType.take_profit_market: 'TAKE_PROFIT_MARKET',
            OrderType.trailing_stop: 'TRAILING_STOP_MARKET'
        }
    }

    @classmethod
    def prefetch_request_data(cls, schema: str, params: dict) -> dict:
        if schema in [OrderSchema.margin, OrderSchema.margin_coin]:
            if params.get('order_type') in ['TRAILING_STOP_MARKET']:
                params['activationPrice'] = params['stop_price']
        return params

    @classmethod
    def prefetch_response_data(cls, schema: str, raw_data: dict) -> dict:
        if schema in [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated]:
            if raw_data['type'].upper() == 'STOP_LOSS' and raw_data.get('trailingDelta'):
                raw_data['type'] = 'TRAILING_STOP_MARKET'
        return raw_data

    @classmethod
    def prefetch_message_data(cls, schema: str, item: dict) -> dict:
        if schema in [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated]:
            if item['o'].upper() == 'STOP_LOSS' and item.get('d'):
                item['o'] = 'TRAILING_STOP_MARKET'
        return item

    @classmethod
    def map_api_parameter_names(cls, schema: str, params: dict, create_params: bool = False) -> Optional[dict]:
        """
        Changes the name (key) of any parameters that have a different name in the Binance API.
        Example: 'ttl' becomes 'timeInForce'

        """
        if schema in [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated]:
            _param_names_map = deepcopy(cls.SPOT_PARAMETER_NAMES_MAP)
        else:
            _param_names_map = deepcopy(cls.FUTURES_PARAMETER_NAMES_MAP)
        tmp_params = {}
        if create_params:
            _param_names_map.update(cls.CREATE_PARAMETER_NAMES_MAP)
        for param, value in params.items():
            if value is None:
                continue
            _param = _param_names_map.get(param) or param
            tmp_params[_param] = value
        return tmp_params

    @classmethod
    def store_type(cls, schema: str, order_type: Optional[str]) -> str:
        if schema in (
                OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated
        ) and order_type in (
                OrderType.stop_market, OrderType.take_profit_market, OrderType.trailing_stop
        ):
            raise ConnectorError(f"Invalid order type: {order_type} with schema: {schema}")
        return super().store_type(schema, order_type)

    @classmethod
    def _store_order_mapping_parameters(cls, exchange_order_type: str, schema: str) -> list:
        data_for_schema = cls._get_mapping_for_schema(schema)
        data = data_for_schema.get(exchange_order_type)
        if data:
            return data['params']
        return data_for_schema['LIMIT']['params']

    @classmethod
    def _assign_custom_parameter_values(cls, schema: str, options: Optional[dict]) -> dict:
        """
        Changes the value of certain parameters according to Binance's specification.

        """
        new_options = {'new_order_resp_type': 'RESULT'}

        if schema in [OrderSchema.exchange, OrderSchema.margin_cross, OrderSchema.margin_isolated]:
            _param_names_map = cls.SPOT_PARAMETER_NAMES_MAP
        else:
            _param_names_map = cls.FUTURES_PARAMETER_NAMES_MAP
        for k, v in options.items():
            if k == 'ttl':
                new_options['ttl'] = _param_names_map.get(v)
            elif k == 'is_passive' and v:
                new_options['ttl'] = _param_names_map.get('GTX')
            else:
                new_options[k] = v
        return new_options

    @classmethod
    def _store_order_additional_parameters(cls, exchange_order_type: str, schema: str) -> dict:
        data_for_schema = cls._get_mapping_for_schema(schema)
        data = data_for_schema.get(exchange_order_type)
        if data:
            return data['additional_params']
        return data_for_schema['LIMIT']['additional_params']

    @classmethod
    def _get_mapping_for_schema(cls, schema: str) -> Optional[dict]:
        """
        Retrieves order type parameter mapping data for the specified schema.

        """
        mapping_data = cls.PARAMETERS_BY_ORDER_TYPE_MAP.get(schema)
        if not mapping_data:
            raise ConnectorError(f"Invalid schema parameter: {schema}")
        return mapping_data
