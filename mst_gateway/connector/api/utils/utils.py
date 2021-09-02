from typing import Union


def convert_to_currency(balances: dict, currency_rate: float):
    new_balances = {}
    for field, value in balances.items():
        try:
            new_balances[field] = value * (1 / currency_rate)
        except TypeError:
            new_balances[field] = 0
    return new_balances


def load_wallet_summary_in_usd(currencies: dict, balances: list, fields: Union[list, tuple], is_for_ws=False):
    _currency_key = 'cur' if is_for_ws else 'currency'
    total_balance = {}
    # init total balance structure if list of balances is empty
    for f in fields:
        total_balance.setdefault(f, 0)
    for b in balances:
        _price = currencies.get(f"{b[_currency_key]}".lower()) or 0
        for f in fields:
            total_balance[f] += _price * (b[f] or 0)
    return total_balance
