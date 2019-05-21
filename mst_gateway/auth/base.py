from abc import ABCMeta, abstractmethod
from ..exceptions import AuthError


def _expired(ttl, period, border=0):
    return ttl is not None and ttl <= period + border


class Auth(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, auth):
        if not isinstance(auth, dict):
            raise AuthError("Auth configuration should be of a dict type")
        self._autorenewable = auth.get('autorenew', False)
        self.ttl = None
        self.max_ttl = None
        self.initial_ttl = None
        self.max_ttl_border = 0
        self.ttl_border = 0

    def init(self):
        pass

    def renew(self):
        # pylint: disable=unused-argument,no-self-use
        return True

    def revoke(self):
        pass

    @property
    def expired(self):
        return False

    @property
    def autorenewable(self):
        return self._autorenewable

    def close(self):
        try:
            self.revoke()
        except AuthError:
            pass

    def clean(self):
        pass

    def expired_in(self, period):
        # ttl will be expired in period seconds
        return _expired(self.ttl, period, self.ttl_border)

    def revoked_in(self, period):
        # max_ttl will be expired in period seconds
        return _expired(self.max_ttl, period, self.max_ttl_border)

    def inc_ttl(self, addend):
        return self.dec_ttl(-addend)

    def inc_max_ttl(self, addend):
        return self.dec_max_ttl(-addend)

    def dec_ttl(self, subtrahend):
        if self.ttl is not None:
            self.ttl -= subtrahend
        self.dec_max_ttl(subtrahend)

    def dec_max_ttl(self, subtrahend):
        if self.max_ttl is not None:
            self.max_ttl -= subtrahend
