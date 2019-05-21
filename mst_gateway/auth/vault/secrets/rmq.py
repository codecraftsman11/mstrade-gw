from .db import Auth as DBAuth
from ....exceptions import AuthError


class Auth(DBAuth):
    def __init__(self, auth):
        if 'uri' not in auth:
            raise AuthError("Vault rmq auth doesn't have uri cfg parameters")
        super().__init__(auth)

    def _get_ttl_uri(self):
        return "{}/config/lease/".format(self._mount)
