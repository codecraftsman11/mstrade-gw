from .base import Auth as VaultKV
from ....login import Auth as AuthLogin
from .....utils import fetch_data


class Auth(VaultKV, AuthLogin):
    def __init__(self, auth):
        super().__init__(auth)
        self._keys = dict(
            user=auth.get('key_user', 'user'),
            password=auth.get('key_password', 'password')
        )

    @property
    def user(self):
        if self._data is None:
            self.init()
        return fetch_data(self._data, self._keys['user'])

    @property
    def password(self):
        if self._data is None:
            self.init()
        return fetch_data(self._data, self._keys['password'])
