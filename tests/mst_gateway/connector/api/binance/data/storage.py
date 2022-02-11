from mst_gateway.connector.api.types import LeverageType, OrderSchema, BUY
from mst_gateway.storage.var import StateStorageKey

STORAGE_DATA = {
    StateStorageKey.symbol: {
        'tbinance': {
            OrderSchema.exchange: {
                'btcusdt': {
                    'tick': 0.01,
                    'pair': ['BTC', 'USDT'],
                    'volume_tick': 1e-06,
                    'max_leverage': None,
                    'schema': OrderSchema.exchange,
                    'expiration': None,
                    'expiration_date': None,
                    'created': '2021-09-06T09:51:21.271836',
                    'extra': {},
                    'system_symbol': 'btcusd',
                    'symbol': 'btcusdt',
                    'exchange': 'tbinance',
                    'wallet_asset': None,
                },
            },
            OrderSchema.margin2: {
                'btcusdt': {
                    'tick': 0.01,
                    'pair': ['BTC', 'USDT'],
                    'volume_tick': 1e-06,
                    'max_leverage': None,
                    'schema': OrderSchema.margin2,
                    'expiration': None,
                    'expiration_date': None,
                    'created': '2021-09-06T09:51:21.271836',
                    'extra': {},
                    'system_symbol': 'btcusd',
                    'symbol': 'btcusdt',
                    'exchange': 'tbinance',
                    'wallet_asset': None,
                },
            },
            OrderSchema.margin3: {
                'btcusdt': {
                    'tick': 0.01,
                    'pair': ['BTC', 'USDT'],
                    'volume_tick': 1e-06,
                    'max_leverage': None,
                    'schema': OrderSchema.margin3,
                    'expiration': None,
                    'expiration_date': None,
                    'created': '2021-09-06T09:51:21.271836',
                    'extra': {},
                    'system_symbol': 'btcusd',
                    'symbol': 'btcusdt',
                    'exchange': 'tbinance',
                    'wallet_asset': None,
                },
            },
            OrderSchema.futures: {
                'btcusdt': {
                    'tick': 0.01,
                    'pair': ['BTC', 'USDT'],
                    'volume_tick': 0.001,
                    'max_leverage': 125.0,
                    'schema': OrderSchema.futures,
                    'expiration': 'None',
                    'expiration_date': 'None',
                    'created': '2021-09-06T09:51:21.272746',
                    'extra': {
                        'leverage_brackets': [
                            {'bracket': 1, 'initialLeverage': 125, 'notionalCap': 50000, 'notionalFloor': 0,
                             'maintMarginRatio': 0.004, 'cum': 0.0},
                            {'bracket': 2, 'initialLeverage': 100, 'notionalCap': 250000, 'notionalFloor': 50000,
                             'maintMarginRatio': 0.005, 'cum': 50.0},
                            {'bracket': 3, 'initialLeverage': 50, 'notionalCap': 1000000, 'notionalFloor': 250000,
                             'maintMarginRatio': 0.01, 'cum': 1300.0},
                            {'bracket': 4, 'initialLeverage': 20, 'notionalCap': 10000000, 'notionalFloor': 1000000,
                             'maintMarginRatio': 0.025, 'cum': 16300.0},
                            {'bracket': 5, 'initialLeverage': 10, 'notionalCap': 20000000, 'notionalFloor': 10000000,
                             'maintMarginRatio': 0.05, 'cum': 266300.0},
                            {'bracket': 6, 'initialLeverage': 5, 'notionalCap': 50000000, 'notionalFloor': 20000000,
                             'maintMarginRatio': 0.1, 'cum': 1266300.0},
                            {'bracket': 7, 'initialLeverage': 4, 'notionalCap': 100000000, 'notionalFloor': 50000000,
                             'maintMarginRatio': 0.125, 'cum': 2516300.0},
                            {'bracket': 8, 'initialLeverage': 3, 'notionalCap': 200000000, 'notionalFloor': 100000000,
                             'maintMarginRatio': 0.15, 'cum': 5016300.0},
                            {'bracket': 9, 'initialLeverage': 2, 'notionalCap': 300000000, 'notionalFloor': 200000000,
                             'maintMarginRatio': 0.25, 'cum': 25016300.0},
                            {'bracket': 10, 'initialLeverage': 1, 'notionalCap': 9223372036854775807,
                             'notionalFloor': 300000000, 'maintMarginRatio': 0.5, 'cum': 100016300.0}
                        ]
                    },
                    'system_symbol': 'btcusd',
                    'symbol': 'btcusdt',
                    'exchange': 'tbinance',
                    'wallet_asset': 'USDT',
                },
            },
            OrderSchema.futures_coin: {
                'btcusd_perp': {
                    'tick': 0.1,
                    'pair': ['BTC', 'USD'],
                    'volume_tick': 1.0,
                    'max_leverage': 125.0,
                    'schema': OrderSchema.futures_coin,
                    'expiration': 'None',
                    'expiration_date': 'None',
                    'created': '2021-09-06T09:51:21.288366',
                    'extra': {
                        'face_price_data': {'contract_size': 100},
                        'leverage_brackets': [
                            {'bracket': 1, 'initialLeverage': 125, 'qtyCap': 5, 'qtyFloor': 0,
                             'maintMarginRatio': 0.004, 'cum': 0.0},
                            {'bracket': 2, 'initialLeverage': 100, 'qtyCap': 10, 'qtyFloor': 5,
                             'maintMarginRatio': 0.005, 'cum': 0.005},
                            {'bracket': 3, 'initialLeverage': 50, 'qtyCap': 20, 'qtyFloor': 10,
                             'maintMarginRatio': 0.01, 'cum': 0.055},
                            {'bracket': 4, 'initialLeverage': 20, 'qtyCap': 50, 'qtyFloor': 20,
                             'maintMarginRatio': 0.025, 'cum': 0.355},
                            {'bracket': 5, 'initialLeverage': 10, 'qtyCap': 100, 'qtyFloor': 50,
                             'maintMarginRatio': 0.05, 'cum': 1.605},
                            {'bracket': 6, 'initialLeverage': 5, 'qtyCap': 200, 'qtyFloor': 100,
                             'maintMarginRatio': 0.1, 'cum': 6.605},
                            {'bracket': 7, 'initialLeverage': 4, 'qtyCap': 400, 'qtyFloor': 200,
                             'maintMarginRatio': 0.125, 'cum': 11.605},
                            {'bracket': 8, 'initialLeverage': 3, 'qtyCap': 1000, 'qtyFloor': 400,
                             'maintMarginRatio': 0.15, 'cum': 21.605},
                            {'bracket': 9, 'initialLeverage': 2, 'qtyCap': 1500, 'qtyFloor': 1000,
                             'maintMarginRatio': 0.25, 'cum': 121.605},
                            {'bracket': 10, 'initialLeverage': 1, 'qtyCap': 9223372036854775807, 'qtyFloor': 1500,
                             'maintMarginRatio': 0.5, 'cum': 496.605}]
                    },
                    'system_symbol': 'btcusd',
                    'symbol': 'btcusd_perp',
                    'exchange': 'tbinance',
                    'wallet_asset': 'BTC',
                },
            },
        },
    },
    f"position.1.tbinance.{OrderSchema.exchange}.btcusdt": {
        'id': '1',
        'symbol': 'btcusdt',
        'side': BUY,
        'volume': 1.0,
        'entry_price': 55555.0,
        'leverage': 1,
        'leverage_type': LeverageType.isolated,
        'action': 'update',
    },
    f"position.1.tbinance.{OrderSchema.margin2}.btcusdt": {
        'id': '1',
        'symbol': 'btcusdt',
        'side': BUY,
        'volume': 1.0,
        'entry_price': 55555.0,
        'leverage': 1,
        'leverage_type': LeverageType.isolated,
        'action': 'update',
    },
    StateStorageKey.exchange_rates: {
        'tbinance': {
            OrderSchema.exchange: {'bnb': 547.9, 'btc': 48736.89, 'eth': 2757.89, 'ltc': 1095.94, 'trx': 0.09164,
                                   'xrp': 0.8234, 'usdt': 1, 'busd': 0.9843693856},
            OrderSchema.futures: {'reef': 0.0202, 'usdt': 1, 'trx': 0.08882, 'skl': 0.2362, 'qtum': 10.01,
                                  'iotx': 0.10816, 'ont': 0.7995, 'ksm': 341.4, 'akro': 0.02533, 'icx': 1.155,
                                  '1000xec': 0.1316, 'celo': 6.0, 'sxp': 2.2534, 'link': 20.409, 'dgb': 0.04952,
                                  'rsr': 0.03669, 'comp': 191.0, 'icp': 32.18, 'sushi': 5.564, 'yfi': 26859.0,
                                  'bnb': 547.99, 'nkn': 0.414, 'doge': 0.17, 'keep': 0.6919, 'btt': 0.003268,
                                  'lpt': 44.57, 'tlm': 0.2569, 'defi': 2703.0, 'alice': 13.296, 'luna': 61.857,
                                  'dent': 0.0044, 'ctk': 1.619, 'ocean': 0.9129, 'atom': 22.5, 'ftm': 1.4141,
                                  'mtl': 1.98, 'ens': 52.84, 'btcdom': 1070.9, 'blz': 0.2644, 'xrp': 0.832,
                                  'gtc': 9.523, 'bts': 0.04227, 'enj': 2.997, 'bat': 0.9968, 'trb': 40.94,
                                  'cvc': 0.38317, 'dash': 133.04, 'mask': 14.3483, 'sfp': 1.6014, 'chz': 0.25996,
                                  'rune': 6.44, 'ltc': 154.97, 'stmx': 0.02373, 'sol': 150.0, 'ata': 0.9792,
                                  'axs': 101.98, 'ren': 0.6685, 'btc211231': 54444.0, 'usdt211231': 1, 'bal': 19.5,
                                  'bel': 2.5803, 'bzrx': 0.3712, 'xmr': 192.69, 'unfi': 9.074, 'zrx': 0.8713,
                                  'rvn': 0.12963, 'eth': 3988.46, 'chr': 0.6518, 'ctsi': 0.8609, 'ar': 44.0,
                                  'coti': 0.32575, 'xtz': 4.559, 'bch': 447.69, 'sc': 0.018905, 'waves': 21.11,
                                  'zil': 0.07028, 'eth211231': 3945.1, '1inch': 3.3, 'audio': 2.38, 'hot': 0.0103,
                                  'aave': 175.0, 'sand': 5.3247, 'yfii': 3401.9, 'egld': 270.0, 'flm': 0.5204,
                                  'ada': 1.2, 'mkr': 2400.3, 'gala': 0.59601, 'nu': 1.1941, 'vet': 0.086,
                                  'fil': 40.0, '1000shib': 0.034171, 'omg': 6.445, 'iost': 0.03, 'klay': 1.3977,
                                  'avax': 78.0, 'ankr': 0.1087, 'lit': 5.005, 'near': 10.0, 'knc': 1.89,
                                  'btc': 48749.66, 'kava': 5.0308, 'snx': 8.4, 'mana': 3.4922, 'dodo': 1.0,
                                  'celr': 0.06785, 'dot': 27.589, 'dydx': 8.287, 'band': 6.794, 'storj': 1.2575,
                                  'ray': 10.62, 'etc': 39.0, 'bake': 1.6672, 'tomo': 2.1887, 'uni': 16.512,
                                  'theta': 4.585, 'lrc': 2.3545, 'grt': 0.74864, 'xem': 0.1355, 'xlm': 0.27136,
                                  'lina': 0.0473, 'hnt': 39.182, 'algo': 1.4237, 'hbar': 0.24943, 'zec': 166.1,
                                  'ogn': 0.6654, 'zen': 61.94, 'neo': 25.823, 'srm': 7.733, 'matic': 1.942,
                                  'c98': 2.19, 'busd': 1.5902205456, 'ftt': 66.6302408606},
            OrderSchema.futures_coin: {'ltc': 265.0, 'usd': 1, 'bch211231': 450.0, 'usd211231': 1, 'gala': 0.59115,
                                       'ada211231': 2.6, 'sol': 145.087, 'btc220325': 62900.0, 'usd220325': 1,
                                       'sand': 2.5447, 'ftm': 2.7606, 'bch': 559.17, 'fil': 54.166, 'link': 27.32,
                                       'avax': 137.07, 'eth': 4707.26, 'bnb': 371.699, 'eos': 5.5, 'luna': 38.0,
                                       'ada': 1.4, 'mana': 3.4276, 'ltc211231': 133.2, 'btc211231': 51497.0,
                                       'eth211231': 3163.05, 'btc': 48776.5}},
    },
    f"{StateStorageKey.state}:wallet.1": {
        OrderSchema.exchange: {'tbl': {'btc': 31.60986648, 'usd': 1530740.97476392}, 'bls': {
            'bnb': {'cur': 'BNB', 'bl': 1000.0, 'wbl': 1000.0, 'mbl': 1000.0, 'im': 0.0,
                    'am': 1000.0, 't': 'hold'},
            'btc': {'cur': 'BTC', 'bl': 0.991, 'wbl': 0.991, 'mbl': 0.991, 'im': 0.0,
                    'am': 0.991, 't': 'hold'},
            'busd': {'cur': 'BUSD', 'bl': 10000.0, 'wbl': 10000.0, 'mbl': 10000.0, 'im': 0.0,
                     'am': 10000.0, 't': 'hold'},
            'eth': {'cur': 'ETH', 'bl': 100.0, 'wbl': 100.0, 'mbl': 100.0, 'im': 0.0,
                    'am': 100.0, 't': 'hold'},
            'ltc': {'cur': 'LTC', 'bl': 500.0, 'wbl': 500.0, 'mbl': 500.0, 'im': 0.0,
                    'am': 500.0, 't': 'hold'},
            'trx': {'cur': 'TRX', 'bl': 500000.0, 'wbl': 500000.0, 'mbl': 500000.0, 'im': 0.0,
                    'am': 500000.0, 't': 'hold'},
            'usdt': {'cur': 'USDT', 'bl': 10873.54038492, 'wbl': 10873.54038492, 'mbl': 10873.54038492,
                     'im': 0.0, 'am': 10873.54038492, 't': 'hold'},
            'xrp': {'cur': 'XRP', 'bl': 50000.0, 'wbl': 50000.0, 'mbl': 50000.0, 'im': 0.0,
                    'am': 50000.0, 't': 'hold'}}}
    },
    f"{StateStorageKey.state}:wallet.2": {
        OrderSchema.futures: {'tre': True, 'tbl': {'btc': 0.20648184, 'usd': 10000.96638768},
                              'tupnl': {'btc': 0.0, 'usd': 0.0}, 'tmbl': {'btc': 0.20648184, 'usd': 10000.96638768},
                              'tbor': {'btc': 0.0, 'usd': 0.0}, 'tist': {'btc': 0.0, 'usd': 0.0}, 'bls': {
                'bnb': {'cur': 'BNB', 'bl': 0.0, 'wbl': 0.0, 'bor': 0.0, 'ist': 0.0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'usdt': {'cur': 'USDT', 'bl': 10000.96638768, 'wbl': 10000.96638768, 'bor': 0.0, 'ist': 0.0,
                         'upnl': 0.0, 'mbl': 10000.96638768, 'mm': 0.0, 'im': 0.0, 'am': 10000.96638768, 't': 'trade'},
                'busd': {'cur': 'BUSD', 'bl': 0.0, 'wbl': 0.0, 'bor': 0.0, 'ist': 0.0, 'upnl': 0.0, 'mbl': 0.0,
                         'mm': 0.0, 'im': 0.0, 'am': 0.0, 't': 'trade'}}},
        OrderSchema.futures_coin: {'tre': True, 'tbl': {'btc': 12.88807193, 'usd': 624669.38071048},
                                   'tupnl': {'btc': -3.6e-07, 'usd': -0.01744877},
                                   'tmbl': {'btc': 12.88807157, 'usd': 624669.36326171},
                                   'tbor': {'btc': 0.0, 'usd': 0.0}, 'tist': {'btc': 0.0, 'usd': 0.0}, 'bls': {
                'btc': {'cur': 'BTC', 'bl': 9.99961585, 'wbl': 9.99951235, 'bor': 0, 'ist': 0, 'upnl': -3.6e-07,
                        'mbl': 9.99961549, 'mm': 8.25e-06, 'im': 0.00010314, 'am': 9.99960724, 't': 'trade'},
                'ada': {'cur': 'ADA', 'bl': 100000.0, 'wbl': 100000.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 100000.0,
                        'mm': 0.0, 'im': 0.0, 'am': 100000.0, 't': 'trade'},
                'link': {'cur': 'LINK', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'doge': {'cur': 'DOGE', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'eth': {'cur': 'ETH', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'bnb': {'cur': 'BNB', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'trx': {'cur': 'TRX', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'dot': {'cur': 'DOT', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'eos': {'cur': 'EOS', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'uni': {'cur': 'UNI', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'ltc': {'cur': 'LTC', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'theta': {'cur': 'THETA', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                          'im': 0.0, 'am': 0.0, 't': 'trade'},
                'bch': {'cur': 'BCH', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'xrp': {'cur': 'XRP', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'xlm': {'cur': 'XLM', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'etc': {'cur': 'ETC', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'fil': {'cur': 'FIL', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'egld': {'cur': 'EGLD', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'sol': {'cur': 'SOL', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'luna': {'cur': 'LUNA', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'ftm': {'cur': 'FTM', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                        'im': 0.0, 'am': 0.0, 't': 'trade'},
                'sand': {'cur': 'SAND', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'mana': {'cur': 'MANA', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'avax': {'cur': 'AVAX', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'gala': {'cur': 'GALA', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                         'im': 0.0, 'am': 0.0, 't': 'trade'},
                'matic': {'cur': 'MATIC', 'bl': 0.0, 'wbl': 0.0, 'bor': 0, 'ist': 0, 'upnl': 0.0, 'mbl': 0.0, 'mm': 0.0,
                          'im': 0.0, 'am': 0.0, 't': 'trade'}}},
    },
}
