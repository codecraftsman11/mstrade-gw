from importlib import import_module
from ...exceptions import ConfigError
from .base import cast


VALIDATOR_TYPES = ('base', 'db', 'amqp', 'vault', 'se', 'mongo', 'auth_approle', 'auth_login',
                   'auth_token', 'auth_vault', 'auth_vault_login')


__all__ = ['cast', 'create_validator']


def create_validator(config, name=None):
    if name is None:
        name = 'base'
    try:
        module = import_module('.' + name, __name__)
    except ImportError as exc:
        raise ConfigError("Error importing validator %s, Details: %s" % (name,
                                                                         exc))
    return module.Validator(config)
