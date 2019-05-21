from .base import Validator as Base, INTEGER


class Validator(Base):
    OBVIOUS_KEYS = ('mount', 'path')

    KEY_TYPES = {
        'version': INTEGER,
    }
