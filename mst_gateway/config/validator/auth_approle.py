from .base import Validator as Base


class Validator(Base):
    OBVIOUS_KEYS = ('mount', 'role', 'secretid', 'roleid', 'autorenew')
