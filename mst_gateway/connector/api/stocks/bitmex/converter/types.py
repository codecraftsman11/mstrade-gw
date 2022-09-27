from typing import Optional


from mst_gateway.connector.api import (
    BaseOrderTypeConverter,
    OrderType,
    OrderSchema,
)


class BitmexOrderTypeConverter(BaseOrderTypeConverter):
    """
    Order type converter for Bitmex

    custom args:
        ordType: TrailingStop
    """
    PARAMETER_NAMES_MAP = {
        'order_id': 'clOrdID',
        'exchange_order_id': 'orderID',
        'stop_price': 'stopPx',
        'volume': 'orderQty',
        'comments': 'text',
        'ttl': 'timeInForce',
        'ttl_type': 'timeInForce',
        'display_value': 'displayQty',
        'order_type': 'ordType',
        'iceberg_volume': 'displayQty',
        'H1': 'GoodTillCancel',
        'H4': 'GoodTillCancel',
        'D1': 'GoodTillCancel',
        'GTC': 'GoodTillCancel',
        'FOK': 'FillOrKill',
        'IOC': 'ImmediateOrCancel',
        'reduce_only': 'ReduceOnly'
    }

    DEFAULT_PARAMETERS = [
        'clOrdID',
        'symbol',
        'ordType',
        'side',
        'orderQty',
        'text'
    ]

    PARAMETERS_BY_ORDER_TYPE_MAP = {
        'Market': {
            'params': [
                *DEFAULT_PARAMETERS
            ],
            'additional_params': {}
        },
        'Limit': {
            'params': [
                *DEFAULT_PARAMETERS,
                'timeInForce',
                'execInst',
                'displayQty',
                'price',
                'ReduceOnly'
            ],
            'additional_params': {}
        },
        'Stop': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPx',
                'execInst',
                'ReduceOnly'
            ],
            'additional_params': {}
        },
        'StopLimit': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPx',
                'price',
                'execInst',
                'ReduceOnly'
            ],
            'additional_params': {}
        },
        'MarketIfTouched': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPx',
                'execInst',
                'ReduceOnly'
            ],
            'additional_params': {}
        },
        'LimitIfTouched': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPx',
                'price',
                'execInst',
                'ReduceOnly'
            ],
            'additional_params': {}
        },
        'TrailingStop': {
            'params': [
                *DEFAULT_PARAMETERS,
                'stopPx',
                'pegOffsetValue',
                'pegPriceType',
                'execInst',
                'ReduceOnly'
            ],
            'additional_params': {
                'pegPriceType': 'TrailingStopPeg',
                'execInst': 'LastPrice',
                'ordType': 'Stop'
            }
        }

    }

    LOAD_TYPE_MAP = {
        OrderSchema.margin: {
            'Market': OrderType.market,
            'Limit': OrderType.limit,
            'Stop': OrderType.stop_market,
            'StopLimit': OrderType.stop_limit,
            'MarketIfTouched': OrderType.take_profit_market,
            'LimitIfTouched': OrderType.take_profit_limit,
            # use TrailingStop if exchange order data contain a pegPriceType field with value "TrailingStopPeg"
            'TrailingStop': OrderType.trailing_stop,
        }
    }

    STORE_TYPE_BY_SCHEMA_MAP = {
        OrderSchema.margin: {
            OrderType.limit: 'Limit',
            OrderType.market: 'Market',
            OrderType.stop_market: 'Stop',
            OrderType.stop_limit: 'StopLimit',
            OrderType.take_profit_limit: 'LimitIfTouched',
            OrderType.take_profit_market: 'MarketIfTouched',
            OrderType.trailing_stop: 'TrailingStop'
        }
    }

    @classmethod
    def prefetch_request_data(cls, schema: str, params: dict) -> dict:
        # TODO: remove mock, calc real pegOffsetValue
        if params.get('order_type') == 'TrailingStop':
            params['pegOffsetValue'] = 100
            if params['side'] == 'Sell':
                params['pegOffsetValue'] *= -100
        return params

    @classmethod
    def prefetch_response_data(cls, schema: str, raw_data: dict) -> dict:
        if raw_data.get('pegPriceType') == 'TrailingStopPeg':
            raw_data['ordType'] = 'TrailingStop'
        return raw_data

    @classmethod
    def prefetch_message_data(cls, schema: str, item: dict) -> dict:
        if item.get('pegPriceType') == 'TrailingStopPeg':
            item['ordType'] = 'TrailingStop'
        return item

    @classmethod
    def generate_parameters_by_order_type(cls, main_params: dict, options: dict, schema: str) -> dict:
        """
        Fetches specific order parameters based on the order_type value and adds them
        to the main parameters.

        """
        order_type = main_params.pop('order_type', None)
        # TODO connect main and options parameters
        exchange_order_type = cls.store_type(schema, order_type)
        mapping_parameters = cls._store_order_mapping_parameters(exchange_order_type)
        options = cls._assign_custom_parameter_values(schema, options)
        all_params = cls.map_api_parameter_names(
            schema,
            {'order_type': exchange_order_type, **main_params, **options}
        )
        new_params = {}
        for param_name in mapping_parameters:
            value = all_params.get(param_name)
            if value:
                new_params[param_name] = value
        new_params.update(
            cls._store_order_additional_parameters(exchange_order_type)
        )
        return new_params

    @classmethod
    def map_api_parameter_names(cls, schema: str, params: dict) -> Optional[dict]:
        """
        Changes the name (key) of any parameters that have a different name in the Bitmex API.
        Example: 'ttl' becomes 'timeInForce'

        """
        tmp_params = {}
        params = cls.prefetch_request_data(schema, params)
        for param, value in params.items():
            if value is None:
                continue
            _param = cls.PARAMETER_NAMES_MAP.get(param) or param
            tmp_params[_param] = value
        return tmp_params
    
    @classmethod
    def _store_order_mapping_parameters(cls, exchange_order_type: str) -> list:
        data = cls.PARAMETERS_BY_ORDER_TYPE_MAP.get(exchange_order_type)
        if data:
            return data['params']
        return cls.PARAMETERS_BY_ORDER_TYPE_MAP['Limit']['params']

    @classmethod
    def _assign_custom_parameter_values(cls, schema: str, options: Optional[dict]) -> dict:
        """
        Changes the value of certain parameters according to Bitmex's specification.

        """
        new_options = {}
        if options is None:
            return new_options

        for k, v in options.items():
            if k == 'ttl':
                new_options['ttl'] = cls.PARAMETER_NAMES_MAP.get(v)
            elif k == 'is_iceberg' and v:
                new_options['iceberg_volume'] = options['iceberg_volume'] or 0
            elif k == 'is_passive' and v:
                new_options['is_passive'] = 'ParticipateDoNotInitiate'
            else:
                new_options[k] = v
        return new_options

    @classmethod
    def _store_order_additional_parameters(cls, exchange_order_type: str) -> dict:
        data = cls.PARAMETERS_BY_ORDER_TYPE_MAP.get(exchange_order_type)
        if data:
            return data['additional_params']
        return cls.PARAMETERS_BY_ORDER_TYPE_MAP['Limit']['additional_params']

