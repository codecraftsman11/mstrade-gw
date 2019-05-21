from .base import Auth as Base


class Auth(Base):
    def __init__(self, auth):
        super().__init__(auth)
        self._user = auth.get('user')
        self._password = auth.get('password')
        self._autorenewable = False

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password
