# pylint: disable=attribute-defined-outside-init
from abc import ABCMeta, abstractmethod
import random
from ..base import Auth as Base
from ...exceptions import AuthError, ConnectorError
from ...connector import vault


def _get_ttl_border(ttl, _from=.5, _till=.66):
    if not ttl:
        return 0
    random.seed()
    return round(random.uniform(ttl * (1 - _till), ttl * (1 - _from)))  # nosec


class Auth(Base):
    # pylint: disable=too-many-instance-attributes
    __metaclass__ = ABCMeta

    def __init__(self, auth):
        super().__init__(auth)
        if 'client' not in auth:
            raise AuthError("Vault auth client instance is undefined")
        if not isinstance(auth['client'], vault.Connector):
            raise AuthError("Vault auth client is not a vault.Connector instance")
        self._autorenewable = auth.get('autorenew', False)
        self._client = auth['client']
        self.clean()

    def init(self):
        response = self._read_creds()
        self._init_lease(
            lease_id=response['lease_id'],
            lease_duration=response['lease_duration'],
            renewable=response['renewable']
        )
        self._setup_max_ttl()

    def _setup_max_ttl(self):
        self._init_max_ttl()
        self.max_ttl_border = _get_ttl_border(self.max_ttl, .6, .8)

    def renew(self):
        if not self._lease_renewable:
            ret = None
        else:
            ret = self._renew_lease()

        if ret:
            self._init_lease(
                lease_id=ret['lease_id'],
                renewable=ret['renewable'],
                lease_duration=ret['lease_duration'])
        else:
            self.clean()
        return ret

    def revoke(self):
        try:
            if not self._revoked():
                self._revoke_lease()
        except ConnectorError as exc:
            raise AuthError("Auth revoking error. Details: %s" % exc)
        finally:
            self.clean()

    def _revoked(self):
        if not self._lease_id:
            return True
        if not self._read_lease(self._lease_id):
            return True
        return False

    def _read_lease(self, lease_id):
        try:
            return self._client.read_lease(lease_id)
        except ConnectorError as exc:
            raise AuthError("Auth lease reading error. Details: %s" % exc)

    def _revoke_lease(self):
        try:
            return self._client.revoke_secret(self._lease_id)
        except ConnectorError as exc:
            raise AuthError("Auth lease revoking error. Details: %s" % exc)

    def _renew_lease(self):
        try:
            return self._client.renew_secret(self._lease_id)
        except ConnectorError as exc:
            raise AuthError("Auth lease renewing error. Details: %s" % exc)

    def clean(self):
        self._init_lease(None, None, None)
        self.max_ttl = None

    def _init_lease(self, lease_id, renewable, lease_duration):
        self._lease_id = lease_id
        self._lease_duration = lease_duration
        self._lease_renewable = renewable
        self.ttl = lease_duration if lease_duration else None
        self.ttl_border = _get_ttl_border(self.ttl, .5, .66)

    def _init_max_ttl(self):
        self.max_ttl = None

    @property
    def expired(self):
        return self._revoked()

    @abstractmethod
    def _read_creds(self):
        return dict(lease_id=None, renewable=None, lease_duration=None)
