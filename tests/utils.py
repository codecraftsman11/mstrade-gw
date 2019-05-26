# pylint: disable=broad-except


def data_valid(data, rules):
    assert set(data.keys()) == set(rules.keys())
    for k in data:
        assert value_valid(data[k], rules[k]), "Invalid {}".format(k)
    return True


def value_valid(value, rule):
    if isinstance(rule, type):
        try:
            return isinstance(value, rule)
        except Exception:
            return False
    if callable(rule):
        return rule(value)
    return True
