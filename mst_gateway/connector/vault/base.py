from abc import abstractmethod, ABCMeta
from ..base import Connector as BaseConnector

VAULT_FIELDS = ('_connector', 'auth', 'logger', '_url', '_is_closing')


class Connector(BaseConnector):
    __metaclass__ = ABCMeta

    def __init__(self, url, auth, logger=None):
        super().__init__(auth, logger)
        self._url = url
        self._connector = None

    def __getattr__(self, name):
        return getattr(self._connector, name)

    def __setattr__(self, name, value):
        if name in VAULT_FIELDS:
            self.__dict__[name] = value
            return
        setattr(self._connector, name, value)

    @abstractmethod
    def renew_secret(self, lease_id):
        pass

    @abstractmethod
    def renew_token(self, token):
        pass

    @abstractmethod
    def read_lease(self, lease_id):
        pass

    @abstractmethod
    def lookup_token(self, token):
        pass

    @abstractmethod
    def revoke_token(self, token):
        pass

    @abstractmethod
    def revoke_secret(self, lease_id):
        pass

    @abstractmethod
    def is_authenticated(self):
        return False

    @abstractmethod
    def auth_approle(self, role_id, secret_id, mount_point="approle"):
        pass

    @abstractmethod
    def write_kv(self, path, mount="kv", version=2, **kwargs):
        pass

    @abstractmethod
    def read_kv(self, path, mount="kv", version=2):
        pass
