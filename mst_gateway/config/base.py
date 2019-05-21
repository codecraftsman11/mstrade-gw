import os
import configparser
from ..exceptions import ConfigError
from ..logging import DEFAULT_LOG_FORMAT
from .validator import create_validator, cast


DEFAULT_PREFIX = "MST_GATEWAY"
SYS_KEYS = ("__driver__", "__type__", "__auth__")

CONNECTOR_DRIVERS = {
    'amqp.rmq': dict(
        module='amqp.pika',
        validator='amqp',
        connector='BlockingConnector',
        defaults={
            'port': 5672,
            'vhost': '/',
            'user': 'guest',
            'password': 'guest'
        }
    ),
    'amqp.rmq_async': dict(
        module='amqp.pika',
        validator='amqp',
        connector='SelectConnector',
        defaults={
            'port': 5672,
            'vhost': '/',
            'user': 'guest',
            'password': 'guest'
        }
    ),
    'db.pgsql': dict(
        module='db.psycopg',
        connector='Psycopg',
        validator='db',
        defaults={
            'port': 5432,
            'user': '',
            'password': ''
        }
    ),
    'db.mysql': dict(
        module='db.mysql',
        connector='MySQL',
        validator='db',
        defaults={
            'port': 3306,
            'user': '',
            'password': ''
        }
    ),
    'mongo.pymongo': dict(
        module='mongo.pymongo',
        connector='Pymongo',
        validator='mongo',
        defaults={
            'host': ["localhost"],
            'port': 27017,
            'replicaset': None
        }
    ),
    'api.bitmex': dict(
        module='api.bitmex.rest',
        connector='BitmexRestApi',
        validator='api_bitmex',
        defaults={
            'timeout': ""
        }
    ),
    'vault': dict(
        module='vault.hvac',
        connector='Hvac',
        validator='vault',
    )
}

AUTH_DRIVERS = {
    'token': dict(
        module='token',
        validator='auth_token',
    ),
    'login': dict(
        module='login',
        validator='auth_login',
    ),
    'db_vault': dict(
        module='vault.secrets.db',
        validator='auth_vault',
        defaults={
            'autorenew': True
        }
    ),
    'rmq_vault': dict(
        module='vault.secrets.rmq',
        validator='auth_vault',
        defaults={
            'autorenew': True
        }
    ),
    'login_vault': dict(
        module='vault.secrets.kv.login',
        validator='auth_vault_kv',
        defaults={
            'mount': "kv",
            'version': 2,
            'key_user': "user",
            'key_password': "password"
        }
    ),
    'token_vault': dict(
        module='vault.secrets.kv.token',
        validator='auth_vault_kv',
        defaults={
            'mount': "kv",
            'version': 2,
            'key_token': "token",
        }
    ),
    'vault_token': dict(
        module='vault.token',
        validator='auth_vault_token',
        defaults={
            'autorenew': True
        }
    ),
    'vault_approle': dict(
        module='vault.approle',
        validator='auth_approle',
        defaults={
            'mount': "approle",
            'role': None,
            'autorenew': True
        }
    ),
}


CONFIG_DEFAULTS = {
    'main': dict(
        loglevel='INFO',
        logfile='STDOUT',
        logformat=DEFAULT_LOG_FORMAT,
        logtimestamp=False,
        logdatefmt=None,
        renewal_period=60
    ),
    'amqp': dict(
        driver='amqp.rmq',
    ),
    'db': dict(
        driver='db.pgsql',
    ),
    'mongo': dict(
        driver='mongo.pymongo',
    ),
    'api': dict(
        driver='api.bitmex'
    ),
    'vault': dict(
        driver='vault',
        token=None
    )
}


def _set_default_values(trg_data, def_values, src_data=None, param=None):
    if src_data is None:
        src_data = trg_data

    for key, val in def_values.items():
        if param is not None and key != param:
            continue
        if key in SYS_KEYS:
            continue
        if key not in src_data:
            trg_data[key] = val


class Config(object):
    def __init__(self, parser=None, env=None, app_prefix=None):
        self._env = dict(os.environ)
        self._data = {}
        self._app_prefix = 'NC_WORKER' if app_prefix is None else app_prefix
        self._validators = {}
        if env is not None:
            self._env.update(env)
        if parser is None:
            self.parser = configparser.ConfigParser(interpolation=None)
        else:
            self.parser = parser

    def __del__(self):
        self._close()

    def _close(self):
        del self.parser

    def data(self, section):
        if section not in self._data:
            raise ConfigError("Section (%s) is not present in config" % section)
        return self._data[section]

    def read(self, *args, **kwargs):
        self._data = {}
        try:
            self.parser.read(*args, **kwargs)
        except Exception:
            raise ConfigError("Can't read config")
        self._normalize()

    def get(self, section, param, default=None, _type=None):
        try:
            data = self.fetch(section)
        except ConfigError:
            return default

        if 'params' not in data:
            return default

        if param not in data['params']:
            return default

        if _type is not None:
            return cast(data['params'][param], _type)
        return data['params'][param]

    def fetch(self, section, defaults=None, prefix=""):
        if section not in self._data:
            raise ConfigError("Section (%s) is not present in config" % section)

        validator = self.get_section_validator(section)
        return validator.read(self._data[section], defaults, prefix)

    def _normalize(self):
        self._validate()
        self._bind_sections()

    def _bind_sections(self):
        for section in self._data:
            self._set_auth(section)

    def _validate(self):
        for section in self.parser.sections():
            self._validate_data(section)

    def _validate_data(self, section):
        raw_data = dict(self.parser[section])
        self._init_section(section, raw_data)
        return self._section_is_valid(section)

    def _init_section(self, section, raw_data):
        self._data[section] = dict(raw_data)
        self._data[section]['_id'] = section
        self._set_driver(section, raw_data)
        self._set_defaults(section, raw_data)
        self._set_env(section)

    def _set_env(self, section=None, param=None, trg_data=None):
        if section == 'main':
            section_prefix = self._app_prefix + "_"
        else:
            section_prefix = self._app_prefix + "_" + section + "_"

        if trg_data is None:
            trg_data = self._data[section]

        for key in trg_data:
            if param is not None and key != param:
                continue
            if key in SYS_KEYS:
                continue
            env_key = (section_prefix + key).replace('.', '_').upper()
            if env_key in self._env:
                trg_data[key] = self._env[env_key]

    def _set_driver(self, section, data):
        if section == 'main':
            return

        if section in CONFIG_DEFAULTS:
            _set_default_values(data, CONFIG_DEFAULTS[section], param='driver')
        self._set_env(section, param='driver', trg_data=data)
        if 'driver' in data:
            driver = data['driver']
        elif section in CONFIG_DEFAULTS:
            driver = CONFIG_DEFAULTS[section]['driver']
        else:
            self._data[section]['__type__'] = "_raw_"
            self._data[section]['__driver__'] = {}
            return

        if driver in CONNECTOR_DRIVERS:
            self._data[section]['__driver__'] = CONNECTOR_DRIVERS[driver]
            self._data[section]['__type__'] = "connector"
            return

        if driver in AUTH_DRIVERS:
            self._data[section]['__driver__'] = AUTH_DRIVERS[driver]
            self._data[section]['__type__'] = "auth"
            return

        raise ConfigError("Invalid driver name (%s) for section (%s)" %
                          (driver, section))

    def _set_auth(self, section):
        if section == 'main':
            return
        if 'auth' not in self._data[section]:
            return
        auth = self._data[section]['auth']
        if auth not in self._data:
            raise ConfigError("Auth (%s) is not found for section (%s)" %
                              (auth, section))
        if self._data[auth].get('__type__') != "auth":
            raise ConfigError("(%s) referenced by (%s) is not of 'auth' type" %
                              (auth, section))
        self._data[section]['__auth__'] = auth

    def _set_defaults(self, section, data):
        if section != 'main' and 'defaults' in self._data[section]['__driver__']:
            _set_default_values(self._data[section],
                                self._data[section]['__driver__']['defaults'],
                                src_data=data)
        if section in CONFIG_DEFAULTS:
            _set_default_values(self._data[section],
                                CONFIG_DEFAULTS[section],
                                src_data=data)

    def _section_is_valid(self, section):
        validator = self.get_section_validator(section)
        return validator.is_valid(self._data[section])

    def get_section_validator(self, section):
        if section == "main":
            validator_type = 'base'
        else:
            validator_type = self._data[section]['__driver__'].get('validator',
                                                                   "base")
        return self._get_validator(validator_type)

    def _get_validator(self, validator_type):
        if validator_type not in self._validators:
            self._validators[validator_type] = create_validator(name=validator_type,
                                                                config=self)
        return self._validators[validator_type]
