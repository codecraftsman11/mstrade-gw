import os
from .base import Config
from ..exceptions import ConfigError


def read_config_file(config_path, parser=None, env=None, app_prefix=None):
    if not os.path.isfile(config_path):
        raise ConfigError("Config file '%s' doesn't exist" % config_path)
    try:
        config = Config(parser, env, app_prefix)
        config.read(config_path)
    except ConfigError:
        raise ConfigError("Can't read configuration from file %s" % config_path)
    return config
