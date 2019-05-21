from . import base


class Validator(base.Validator):
    OBVIOUS_KEYS = ('url', 'auth')

    KEY_TYPES = {
        'timeout': base.INTEGER
    }
