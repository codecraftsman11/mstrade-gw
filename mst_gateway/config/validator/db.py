from .base import Validator as Base, INTEGER


class Validator(Base):
    OBVIOUS_KEYS = ('host', 'port', 'dbname', 'auth')

    KEY_TYPES = {
        'port': INTEGER,
    }
