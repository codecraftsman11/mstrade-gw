from .base import Validator as Base, INTEGER, LIST


class Validator(Base):
    OBVIOUS_KEYS = ('host', 'port', 'replicaset', 'auth')

    KEY_TYPES = {
        'port': INTEGER,
        'host': LIST
    }
