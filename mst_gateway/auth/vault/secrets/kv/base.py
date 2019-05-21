from ...base import Auth as VaultBase
from .....exceptions import AuthError, ConnectorError


class Auth(VaultBase):
    def __init__(self, auth):
        super().__init__(auth)
        if 'path' not in auth:
            raise AuthError("Path of vault login auth is not defined")
        self._path = auth['path']
        self._mount = auth.get('mount', "kv")
        self._version = auth.get('version', 2)
        self._autorenewable = True
        self._data = None

    def _read_creds(self):
        try:
            response = self._client.read_kv(path=self._path, mount=self._mount,
                                            version=self._version)
        except ConnectorError as exc:
            raise AuthError("Error in vault response. Details: {}".format(exc))
        if not response:
            raise AuthError("Empty response at vault path: %s/%s"
                            % (self._mount, self._path))
        self._data = response['data']
        return dict(
            lease_id=None,
            lease_duration=None,
            renewable=None
        )

    def clean(self):
        super().clean()
        self._data = None
