"""
Vault authentication token provider
"""
from .base import Auth as Base
from ..token import Auth as TokenAuth
from ...exceptions import ConnectorError, AuthError


class Auth(Base, TokenAuth):
    def __init__(self, auth):
        super().__init__(auth)
        self._token = auth.get('token')

    def _revoke_lease(self):
        try:
            return self._client.revoke_token(self._token)
        except ConnectorError as exc:
            raise AuthError("Auth token revoking error. Details: %s" % exc)

    def _read_creds(self):
        return self._read_lease(self._token)

    def _read_lease(self, lease_id):
        data = self._client.lookup_token(lease_id)
        if not data:
            raise AuthError("Vault can't lookup provided token {}".format(lease_id))
        return {'lease_id': data['data']['id'],
                'lease_duration': data['data']['ttl'],
                'renewable': data['data']['renewable']}

    def _renew_lease(self):
        try:
            data = self._client.renew_token(self._token)
        except ConnectorError as exc:
            raise AuthError("Auth token renewing error. Details: %s" % exc)
        if not data:
            return None
        return dict(lease_id=data['auth']['client_token'],
                    lease_duration=data['auth']['lease_duration'],
                    renewable=data['auth']['renewable'])
