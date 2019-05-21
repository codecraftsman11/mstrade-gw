# pylint:disable=no-self-use,unused-argument
from ...exceptions import ConfigError

INTERNAL_FIELDS = ('__driver__', '__auth__', '__type__', 'driver', 'auth', '_id')

STRING = 0
BOOLEAN = 1
INTEGER = 2
LIST = 3


def fetch_driver(data):
    return {key: val for key, val in data['__driver__'].items() if key not in
            ('defaults', 'validator')}


def cast(value, _type):
    if _type == BOOLEAN:
        return _str2bool(value)
    if _type == INTEGER:
        return _str2int(value)
    if _type == LIST:
        return _str2list(value)
    return value


def _str2bool(value):
    if isinstance(value, bool):
        return value
    return value.lower() in ("yes", "true", "t", "1", "y")


def _str2int(value):
    if isinstance(value, int):
        return value
    if value.strip() == "":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(exc)


def _str2list(value):
    if isinstance(value, list):
        return value
    return list(map(lambda x: x.strip(), value.split(',')))


class Validator(object):
    OBVIOUS_KEYS = ()

    KEY_TYPES = {
        'autorenew': BOOLEAN,
        'renewal_period': INTEGER,
        'logtimestamp': BOOLEAN
    }

    def __init__(self, config):
        self._config = config

    def is_valid(self, section_data, defaults=None):
        if defaults is None:
            defaults = {}
        for key in self.OBVIOUS_KEYS:
            if key in defaults:
                continue
            if key not in section_data:
                return False
        return True

    def read(self, section_data, defaults=None, prefix=""):
        data = dict(section_data)
        self._move_defaults(data, defaults, prefix)
        result = {}
        if '__driver__' in data and data['__type__'] != "_raw_":
            result['driver'] = fetch_driver(data)
        if '__auth__' in data:
            result['auth'] = self._config.fetch(data['__auth__'], data,
                                                prefix="auth_")
        result['params'] = self.fetch_params(data)
        result['_id'] = data['_id']
        return result

    def _move_defaults(self, data, defaults, prefix=""):
        if defaults is None:
            defaults = {}
        for key in self.__class__.OBVIOUS_KEYS:
            pkey = prefix + key
            if key not in data:
                if pkey in defaults:
                    data[key] = defaults[pkey]
                else:
                    data[key] = defaults.get(key)
            if pkey in defaults:
                del defaults[pkey]
            elif key in defaults:
                del defaults[key]

    def _fill_defaults(self, data, defaults):
        if defaults is None:
            defaults = {}
        self._move_defaults(data, dict(defaults))

    def fetch_params(self, data):
        return {key: self._get(data, key) for key in data if key not in
                INTERNAL_FIELDS}

    def _get(self, data, key):
        if key in self.__class__.KEY_TYPES:
            return cast(data[key], self.__class__.KEY_TYPES[key])
        return data[key]
