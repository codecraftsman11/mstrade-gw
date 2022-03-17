from typing import Union
from mst_gateway.connector.api.types import OrderSchema, ExchangeDrivers


def to_exchange_asset(driver: str, schema: str, asset: str) -> str:
    asset = asset.lower()
    if driver == ExchangeDrivers.bitmex and schema == OrderSchema.margin and asset == 'btc':
        return 'xbt'
    if schema != OrderSchema.margin_coin and asset == 'usd':
        return 'usdt'
    return asset


def init_summary(summary: dict, fields: iter) -> None:
    for f in fields:
        summary.setdefault(f"total_{f}", {})['usd'] = 0.0


def load_wallet_summary_in_usd(balances: list, fields: iter, exchange_rates: dict, is_for_ws: bool = False) -> dict:
    summary = {}
    init_summary(summary, fields)
    _currency_key = 'cur' if is_for_ws else 'currency'
    for b in balances:
        _price = exchange_rates.get(b[_currency_key].lower()) or 0.0
        for f in fields:
            summary[f"total_{f}"]['usd'] += _price * (b.get(f) or 0.0)
    return summary


def load_wallet_summary(driver: str, schema: str, balances: list, fields: iter, exchange_rates: dict, assets: iter,
                        is_for_ws: bool = False) -> dict:
    wallet_summary = {}
    _summary_in_usd = load_wallet_summary_in_usd(balances, fields, exchange_rates, is_for_ws)
    for _summary_key in _summary_in_usd.keys():
        _value_in_usd = _summary_in_usd[_summary_key]['usd']
        for currency in assets:
            _exchange_rate = exchange_rates.get(to_exchange_asset(driver, schema, currency))
            try:
                wallet_summary.setdefault(_summary_key, {})[currency] = round(_value_in_usd * (1 / _exchange_rate), 8)
            except TypeError:
                wallet_summary.setdefault(_summary_key, {})[currency] = 0.0
    return wallet_summary


def load_wallet_summary_margin_isolated_in_usd(currencies: dict, balances: list,
                                               fields: Union[list, tuple], is_for_ws=False):
    _currency_key = 'cur' if is_for_ws else 'currency'
    total_balance = {}
    # init total balance structure if list of balances is empty
    for f in fields:
        total_balance.setdefault(f, 0.0)
    for b in balances:
        for assets in b.values():
            _price_base = currencies.get(f"{assets['base_asset'][_currency_key]}".lower()) or 0.0
            _price_quote = currencies.get(f"{assets['quote_asset'][_currency_key]}".lower()) or 0.0
            for f in fields:
                total_balance[f] += _price_base * (assets['base_asset'].get(f) or 0.0)
                total_balance[f] += _price_quote * (assets['quote_asset'].get(f) or 0.0)
    return total_balance
