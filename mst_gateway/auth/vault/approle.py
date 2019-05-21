# pylint: disable=attribute-defined-outside-init
from .token import Auth as VaultTokenAuth
from ...exceptions import AuthError, ConnectorError


class Auth(VaultTokenAuth):
    def __init__(self, auth):
        super().__init__(auth)
        self._role_id = auth.get('roleid')
        self._secret_id = auth.get('secretid')
        self._mount = auth.get('mount', "approle")
        self._role = auth.get("role")

    @property
    def token(self):
        if not self._lease_id:
            self.init()
        return self._lease_id

    def _read_creds(self):
        try:
            response = self._client.auth_approle(role_id=self._role_id,
                                                 secret_id=self._secret_id,
                                                 mount_point=self._mount)
        except ConnectorError as exc:
            raise AuthError("Error in vault response. Details: {}".format(exc))
        if not response:
            raise AuthError("Invalid vault approle role_id: {}".format(self._role_id))
        return dict(
            lease_id=response['auth']['client_token'],
            lease_duration=response['auth']['lease_duration'],
            renewable=response['auth']['renewable']
        )

    def _init_max_ttl(self):
        self.max_ttl = None
        if self._role is None:
            return
        try:
            response = self._client.read("auth/{}/role/{}".format(self._mount, self._role))
        except ConnectorError:
            response = None
        if response and response['data']['token_max_ttl']:
            self.max_ttl = response['data']['token_max_ttl']

    def clean(self):
        super().clean()
        self._token = None
