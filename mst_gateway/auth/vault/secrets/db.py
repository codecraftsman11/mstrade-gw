from ..base import Auth as VaultBase
from ...login import Auth as AuthLogin
from ....exceptions import AuthError, ConnectorError


class Auth(VaultBase, AuthLogin):
    def __init__(self, auth):
        super().__init__(auth)
        if 'uri' not in auth:
            raise AuthError("Vault db auth doesn't have uri cfg parameters")
        self._mount, self._role = self._fetch_data(auth.get('uri'))
        self._user = None
        self._password = None

    def _fetch_data(self, uri):
        # pylint: disable=no-self-use
        uri_nodes = uri.split('/')
        if len(uri_nodes) < 3:
            raise AuthError("Invalid uri for db_auth: '%s'" % uri)
        mount = '/'.join(uri_nodes[0:-2])
        role = uri_nodes[-1]
        return (mount, role)

    def _get_creds_uri(self):
        return "{}/creds/{}".format(self._mount, self._role)

    def _get_ttl_uri(self):
        return "{}/roles/{}".format(self._mount, self._role)

    def _read_creds(self):
        try:
            response = self._client.read(self._get_creds_uri())
        except ConnectorError as exc:
            raise AuthError("Error in vault response. Details: {}".format(exc))
        if not response:
            raise AuthError("Empty response at auth vault path: %s"
                            % self._get_creds_uri())
        self._user = response['data'].get('username')
        self._password = response['data'].get('password')
        return dict(
            lease_id=response['lease_id'],
            lease_duration=response['lease_duration'],
            renewable=response['renewable']
        )

    def _init_max_ttl(self):
        self.max_ttl = None
        try:
            response = self._client.read(self._get_ttl_uri())
        except ConnectorError:
            response = None
        if response and response['data']['max_ttl']:
            self.max_ttl = response['data']['max_ttl']

    @property
    def user(self):
        if self._lease_id is None:
            self.init()
        return self._user

    @property
    def password(self):
        if self._lease_id is None:
            self.init()
        return self._password

    def clean(self):
        super().clean()
        self._user = None
        self._password = None
