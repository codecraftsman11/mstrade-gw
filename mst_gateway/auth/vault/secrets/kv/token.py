from .base import Auth as VaultKV
from ....token import Auth as AuthToken
from .....utils import fetch_data


class Auth(VaultKV, AuthToken):
    def __init__(self, auth):
        super().__init__(auth)
        self._keys = dict(
            token=auth.get('key_token', 'token'),
        )

    @property
    def token(self):
        if self._data is None:
            self.init()
        return fetch_data(self._data, self._keys['token'])
