from mst_gateway.connector.api.types import OrderSchema
from mst_gateway.storage.var import StateStorageKey

STORAGE_DATA = {
    f"{StateStorageKey.symbol}.tbinance.{OrderSchema.exchange}": {
        'btcusdt': {'tick': 0.01, 'pair': ['BTC', 'USDT'], 'volume_tick': 1e-06, 'max_leverage': None,
                    'schema': OrderSchema.exchange, 'expiration': None, 'expiration_date': None,
                    'created': '2022-06-30T08:39:27.575230', 'extra': {}, 'wallet_asset': None,
                    'system_symbol': 'btcusdt', 'symbol': 'btcusdt', 'exchange': 'tBinance'},
        'xrpusdt': {'tick': 0.0001, 'pair': ['XRP', 'USDT'], 'volume_tick': 0.1, 'max_leverage': None,
                    'schema': OrderSchema.exchange, 'expiration': None, 'expiration_date': None,
                    'created': '2022-06-30T08:39:27.575476', 'extra': {}, 'wallet_asset': None,
                    'system_symbol': 'xrpusdt', 'symbol': 'xrpusdt', 'exchange': 'tBinance'},
        'ltcusdt': {'tick': 0.01, 'pair': ['LTC', 'USDT'], 'volume_tick': 1e-05, 'max_leverage': None,
                    'schema': OrderSchema.exchange, 'expiration': None, 'expiration_date': None,
                    'created': '2022-06-30T08:39:27.575353', 'extra': {}, 'wallet_asset': None,
                    'system_symbol': 'ltcusdt', 'symbol': 'ltcusdt', 'exchange': 'tBinance'}
    },
    f"{StateStorageKey.symbol}.tbinance.{OrderSchema.margin_cross}": {
        'btcusdt': {
            'tick': 0.01,
            'pair': ['BTC', 'USDT'],
            'volume_tick': 1e-06,
            'max_leverage': None,
            'schema': OrderSchema.margin_cross,
            'expiration': None,
            'expiration_date': None,
            'created': '2022-06-30T08:39:27.575230',
            'extra': {},
            'system_symbol': 'btcusdt',
            'symbol': 'btcusdt',
            'exchange': 'tbinance',
            'wallet_asset': None,
        }
    },
    f"{StateStorageKey.symbol}.tbinance.{OrderSchema.margin_isolated}": {
        'btcusdt': {
            'tick': 0.01,
            'pair': ['BTC', 'USDT'],
            'volume_tick': 1e-06,
            'max_leverage': None,
            'schema': OrderSchema.margin_isolated,
            'expiration': None,
            'expiration_date': None,
            'created': '2022-06-30T08:39:27.575230',
            'extra': {},
            'system_symbol': 'btcusdt',
            'symbol': 'btcusdt',
            'exchange': 'tbinance',
            'wallet_asset': None,
        }
    },
    f"{StateStorageKey.symbol}.tbinance.{OrderSchema.margin}": {
        'btcusdt': {
            'tick': 0.1, 'pair': ['BTC', 'USDT'], 'volume_tick': 0.001, 'max_leverage': 25.0,
            'schema': OrderSchema.margin, 'expiration': None, 'expiration_date': None,
            'created': '2022-06-30T08:39:27.576033', 'extra': {
                'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 25.0, 'notional_cap': 50000.0, 'notional_floor': 0.0,
                     'maint_margin_ratio': 0.01, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 25.0, 'notional_cap': 250000.0, 'notional_floor': 50000.0,
                     'maint_margin_ratio': 0.02, 'cum': 500.0},
                    {'bracket': 3, 'initial_leverage': 10.0, 'notional_cap': 1000000.0, 'notional_floor': 250000.0,
                     'maint_margin_ratio': 0.05, 'cum': 8000.0},
                    {'bracket': 4, 'initial_leverage': 5.0, 'notional_cap': 2000000.0, 'notional_floor': 1000000.0,
                     'maint_margin_ratio': 0.1, 'cum': 58000.0},
                    {'bracket': 5, 'initial_leverage': 4.0, 'notional_cap': 5000000.0, 'notional_floor': 2000000.0,
                     'maint_margin_ratio': 0.125, 'cum': 108000.0},
                    {'bracket': 6, 'initial_leverage': 3.0, 'notional_cap': 10000000.0, 'notional_floor': 5000000.0,
                     'maint_margin_ratio': 0.1665, 'cum': 315500.0},
                    {'bracket': 7, 'initial_leverage': 2.0, 'notional_cap': 15000000.0, 'notional_floor': 10000000.0,
                     'maint_margin_ratio': 0.25, 'cum': 1150500.0},
                    {'bracket': 8, 'initial_leverage': 1.0, 'notional_cap': 50000000.0, 'notional_floor': 15000000.0,
                     'maint_margin_ratio': 0.5, 'cum': 4900500.0}]
            },
            'wallet_asset': 'USDT', 'system_symbol': 'btcusdt', 'symbol': 'btcusdt', 'exchange': 'tBinance'},
        'xrpusdt': {
            'tick': 0.0001, 'pair': ['XRP', 'USDT'], 'volume_tick': 0.1, 'max_leverage': 75.0,
            'schema': OrderSchema.margin,  'expiration': None, 'expiration_date': None,
            'created': '2022-06-30T08:39:27.576365', 'extra': {
                'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 75.0, 'notional_cap': 10000.0, 'notional_floor': 0.0,
                     'maint_margin_ratio': 0.0065, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 50.0, 'notional_cap': 50000.0, 'notional_floor': 10000.0,
                     'maint_margin_ratio': 0.01, 'cum': 35.0},
                    {'bracket': 3, 'initial_leverage': 25.0, 'notional_cap': 250000.0, 'notional_floor': 50000.0,
                     'maint_margin_ratio': 0.02, 'cum': 535.0},
                    {'bracket': 4, 'initial_leverage': 10.0, 'notional_cap': 1000000.0, 'notional_floor': 250000.0,
                     'maint_margin_ratio': 0.05, 'cum': 8035.0},
                    {'bracket': 5, 'initial_leverage': 5.0, 'notional_cap': 2000000.0, 'notional_floor': 1000000.0,
                     'maint_margin_ratio': 0.1, 'cum': 58035.0},
                    {'bracket': 6, 'initial_leverage': 4.0, 'notional_cap': 5000000.0, 'notional_floor': 2000000.0,
                     'maint_margin_ratio': 0.125, 'cum': 108035.0},
                    {'bracket': 7, 'initial_leverage': 3.0, 'notional_cap': 10000000.0, 'notional_floor': 5000000.0,
                     'maint_margin_ratio': 0.15, 'cum': 233035.0},
                    {'bracket': 8, 'initial_leverage': 2.0, 'notional_cap': 9.223372036854776e+18,
                     'notional_floor': 10000000.0, 'maint_margin_ratio': 0.25, 'cum': 1233035.0}]
            },
            'wallet_asset': 'USDT', 'system_symbol': 'xrpusdt', 'symbol': 'xrpusdt', 'exchange': 'tBinance'},
        'ltcusdt': {
            'tick': 0.01, 'pair': ['LTC', 'USDT'], 'volume_tick': 0.001, 'max_leverage': 75.0,
            'schema': OrderSchema.margin, 'expiration': None, 'expiration_date': None,
            'created': '2022-06-30T08:39:27.576569', 'extra': {
                'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 75.0, 'notional_cap': 10000.0, 'notional_floor': 0.0,
                     'maint_margin_ratio': 0.0065, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 50.0, 'notional_cap': 50000.0, 'notional_floor': 10000.0,
                     'maint_margin_ratio': 0.01, 'cum': 35.0},
                    {'bracket': 3, 'initial_leverage': 25.0, 'notional_cap': 250000.0, 'notional_floor': 50000.0,
                     'maint_margin_ratio': 0.02, 'cum': 535.0},
                    {'bracket': 4, 'initial_leverage': 10.0, 'notional_cap': 1000000.0, 'notional_floor': 250000.0,
                     'maint_margin_ratio': 0.05, 'cum': 8035.0},
                    {'bracket': 5, 'initial_leverage': 5.0, 'notional_cap': 2000000.0, 'notional_floor': 1000000.0,
                     'maint_margin_ratio': 0.1, 'cum': 58035.0},
                    {'bracket': 6, 'initial_leverage': 4.0, 'notional_cap': 5000000.0, 'notional_floor': 2000000.0,
                     'maint_margin_ratio': 0.125, 'cum': 108035.0},
                    {'bracket': 7, 'initial_leverage': 3.0, 'notional_cap': 10000000.0, 'notional_floor': 5000000.0,
                     'maint_margin_ratio': 0.15, 'cum': 233035.0},
                    {'bracket': 8, 'initial_leverage': 2.0, 'notional_cap': 9.223372036854776e+18,
                     'notional_floor': 10000000.0, 'maint_margin_ratio': 0.25, 'cum': 1233035.0}]
            },
            'wallet_asset': 'USDT', 'system_symbol': 'ltcusdt', 'symbol': 'ltcusdt', 'exchange': 'tBinance'}
    },
    f"{StateStorageKey.symbol}.tbinance.{OrderSchema.margin_coin}": {
        'btcusd_perp': {
            'tick': 0.1, 'pair': ['BTC', 'USD'], 'volume_tick': 1.0, 'max_leverage': 125.0,
            'schema': OrderSchema.margin_coin, 'expiration': None, 'expiration_date': None,
            'created': '2022-08-02T13:21:45.703245', 'extra': {
                'face_price_data': {'contract_size': 100}, 'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 125.0, 'qty_cap': 5.0, 'qty_floor': 0.0,
                     'maint_margin_ratio': 0.004, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 100.0, 'qty_cap': 10.0, 'qty_floor': 5.0,
                     'maint_margin_ratio': 0.005, 'cum': 0.005},
                    {'bracket': 3, 'initial_leverage': 50.0, 'qty_cap': 20.0, 'qty_floor': 10.0,
                     'maint_margin_ratio': 0.01, 'cum': 0.055},
                    {'bracket': 4, 'initial_leverage': 20.0, 'qty_cap': 50.0, 'qty_floor': 20.0,
                     'maint_margin_ratio': 0.025, 'cum': 0.355},
                    {'bracket': 5, 'initial_leverage': 10.0, 'qty_cap': 100.0, 'qty_floor': 50.0,
                     'maint_margin_ratio': 0.05, 'cum': 1.605},
                    {'bracket': 6, 'initial_leverage': 5.0, 'qty_cap': 200.0, 'qty_floor': 100.0,
                     'maint_margin_ratio': 0.1, 'cum': 6.605},
                    {'bracket': 7, 'initial_leverage': 4.0, 'qty_cap': 400.0, 'qty_floor': 200.0,
                     'maint_margin_ratio': 0.125, 'cum': 11.605},
                    {'bracket': 8, 'initial_leverage': 3.0, 'qty_cap': 1000.0, 'qty_floor': 400.0,
                     'maint_margin_ratio': 0.15, 'cum': 21.605},
                    {'bracket': 9, 'initial_leverage': 2.0, 'qty_cap': 1500.0, 'qty_floor': 1000.0,
                     'maint_margin_ratio': 0.25, 'cum': 121.605},
                    {'bracket': 10, 'initial_leverage': 1.0, 'qty_cap': 9.223372036854776e+18, 'qty_floor': 1500.0,
                     'maint_margin_ratio': 0.5, 'cum': 496.605}]
            },
            'wallet_asset': 'BTC', 'system_symbol': 'btcusd', 'symbol': 'btcusd_perp', 'exchange': 'tBinance'},
        'xrpusd_perp': {
            'tick': 0.0001, 'pair': ['XRP', 'USD'], 'volume_tick': 1.0, 'max_leverage': 20.0,
            'schema': OrderSchema.margin_coin, 'expiration': None, 'expiration_date': None,
            'created': '2022-08-02T13:21:45.704315', 'extra': {
                'face_price_data': {'contract_size': 10}, 'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 20.0, 'qty_cap': 500000.0, 'qty_floor': 0.0,
                     'maint_margin_ratio': 0.023, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 10.0, 'qty_cap': 1000000.0, 'qty_floor': 500000.0,
                     'maint_margin_ratio': 0.043, 'cum': 10000.0},
                    {'bracket': 3, 'initial_leverage': 7.0, 'qty_cap': 1500000.0, 'qty_floor': 1000000.0,
                     'maint_margin_ratio': 0.05, 'cum': 17000.0},
                    {'bracket': 4, 'initial_leverage': 6.0, 'qty_cap': 2000000.0, 'qty_floor': 1500000.0,
                     'maint_margin_ratio': 0.05, 'cum': 17000.0},
                    {'bracket': 5, 'initial_leverage': 5.0, 'qty_cap': 3000000.0, 'qty_floor': 2000000.0,
                     'maint_margin_ratio': 0.1, 'cum': 117000.0},
                    {'bracket': 6, 'initial_leverage': 4.0, 'qty_cap': 5000000.0, 'qty_floor': 3000000.0,
                     'maint_margin_ratio': 0.125, 'cum': 192000.0},
                    {'bracket': 7, 'initial_leverage': 3.0, 'qty_cap': 10000000.0, 'qty_floor': 5000000.0,
                     'maint_margin_ratio': 0.15, 'cum': 317000.0},
                    {'bracket': 8, 'initial_leverage': 2.0, 'qty_cap': 9.223372036854776e+18, 'qty_floor': 10000000.0,
                     'maint_margin_ratio': 0.25, 'cum': 1317000.0}]
            },
            'wallet_asset': 'XRP', 'system_symbol': 'xrpusd', 'symbol': 'xrpusd_perp', 'exchange': 'tBinance'},
        'ltcusd_perp': {
            'tick': 0.01, 'pair': ['LTC', 'USD'], 'volume_tick': 1.0, 'max_leverage': 20.0,
            'schema': OrderSchema.margin_coin, 'expiration': None, 'expiration_date': None,
            'created': '2022-08-02T13:21:45.704173', 'extra': {
                'face_price_data': {'contract_size': 10}, 'leverage_brackets': [
                    {'bracket': 1, 'initial_leverage': 20.0, 'qty_cap': 5000.0, 'qty_floor': 0.0,
                     'maint_margin_ratio': 0.023, 'cum': 0.0},
                    {'bracket': 2, 'initial_leverage': 10.0, 'qty_cap': 10000.0, 'qty_floor': 5000.0,
                     'maint_margin_ratio': 0.043, 'cum': 100.0},
                    {'bracket': 3, 'initial_leverage': 7.0, 'qty_cap': 20000.0, 'qty_floor': 10000.0,
                     'maint_margin_ratio': 0.05, 'cum': 170.0},
                    {'bracket': 4, 'initial_leverage': 6.0, 'qty_cap': 50000.0, 'qty_floor': 20000.0,
                     'maint_margin_ratio': 0.05, 'cum': 170.0},
                    {'bracket': 5, 'initial_leverage': 5.0, 'qty_cap': 100000.0, 'qty_floor': 50000.0,
                     'maint_margin_ratio': 0.1, 'cum': 2670.0},
                    {'bracket': 6, 'initial_leverage': 4.0, 'qty_cap': 150000.0, 'qty_floor': 100000.0,
                     'maint_margin_ratio': 0.125, 'cum': 5170.0},
                    {'bracket': 7, 'initial_leverage': 3.0, 'qty_cap': 200000.0, 'qty_floor': 150000.0,
                     'maint_margin_ratio': 0.15, 'cum': 8920.0},
                    {'bracket': 8, 'initial_leverage': 2.0, 'qty_cap': 9.223372036854776e+18, 'qty_floor': 200000.0,
                     'maint_margin_ratio': 0.25, 'cum': 28920.0}]
            },
            'wallet_asset': 'LTC', 'system_symbol': 'ltcusd', 'symbol': 'ltcusd_perp', 'exchange': 'tBinance'}
    }
}
