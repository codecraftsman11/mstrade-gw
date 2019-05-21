from .base import Auth as Base


class Auth(Base):
    def __init__(self, auth):
        super().__init__(auth)
        self._token = auth.get('token')
        self._autorenewable = False

    @property
    def token(self):
        return self._token
