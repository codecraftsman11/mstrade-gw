# pylint:disable=broad-except

import hvac
from .base import Connector
from .exceptions import VaultError
from ...auth.token import Auth as TokenAuth


class Hvac(Connector):
    def _connect(self, **kwargs):
        self._connector = hvac.Client(self._url)
        self.logger.info("Client of vault server %s is initialized", self._url)
        if isinstance(self.auth, TokenAuth):
            self._connector.token = self.auth.token
            self.logger.debug("Vault token is taken from auth")
        return self._connector

    def _close(self):
        if not self._connector:
            return
        try:
            is_auth = self.is_authenticated()
        except Exception:
            is_auth = False
        try:
            if is_auth:
                self._connector.logout()
                self._connector.adapter.close()
                self.logger.debug("Hvac connection to vault server %s is closed", self._url)
        except Exception as exc:
            raise VaultError("Vault connector close error. Details: %s" % exc)
        finally:
            self._connector = None

    def read_lease(self, lease_id):
        try:
            return self._connector.sys.read_lease(lease_id)
        except hvac.exceptions.VaultError:
            return None
        except Exception as exc:
            raise VaultError("Vault lease read error. Details: %s" % exc)

    def lookup_token(self, token):
        try:
            return self._connector.lookup_token(token)
        except hvac.exceptions.VaultError:
            return None
        except Exception as exc:
            raise VaultError("Vault secret renewal error. Details: %s" % exc)

    def renew_secret(self, lease_id):
        try:
            self.logger.info("Renewing lease %s", lease_id)
            return self._connector.sys.renew_lease(lease_id)
        except hvac.exceptions.VaultError:
            return None
        except Exception as exc:
            raise VaultError("Vault secret renewal error. Details: %s" % exc)

    def renew_token(self, token=None):
        try:
            self.logger.info("Renewing vault token")
            return self._connector.renew_token(token)
        except hvac.exceptions.VaultError:
            return None
        except Exception as exc:
            raise VaultError("Vault token renewal error. Details: %s" % exc)

    def revoke_token(self, token):
        try:
            self.logger.info("Revoking vault token")
            self._connector.revoke_token(token)
        except hvac.exceptions.VaultError:
            pass
        except Exception as exc:
            raise VaultError("Vault token revoking error. Details: %s" % exc)
        return True

    def revoke_secret(self, lease_id):
        try:
            self.logger.info("Revoking lease %s", lease_id)
            self._connector.sys.revoke_lease(lease_id)
        except Exception as exc:
            raise VaultError("Vault secret revoking error. Details: %s"
                             % exc)
        return True

    def is_authenticated(self):
        if not self._connector:
            return False
        try:
            return self._connector.is_authenticated()
        except Exception as exc:
            raise VaultError("Vault authentication check error. Details:"
                             " %s" % exc)

    def read(self, uri):
        try:
            self.logger.info("Reading path %s", uri)
            return self._connector.read(uri)
        except Exception as exc:
            raise VaultError("Vault read request error. Details:"
                             " %s" % exc)

    def auth_approle(self, role_id, secret_id, mount_point="approle"):
        try:
            self.logger.info("Authenticating via approle")
            return self._connector.auth_approle(role_id=role_id,
                                                secret_id=secret_id,
                                                mount_point=mount_point)
        except Exception as exc:
            raise VaultError("Vault approle authentication error. Details:"
                             " %s" % exc)

    def write_kv(self, path, mount="kv", version=2, **kwargs):
        try:
            self.logger.info("Writing secret %s/%s", mount, path)
            if version == 2:
                self._write_kv_2(path, mount, **kwargs)
            else:
                self._write_kv_1(path, mount, **kwargs)
        except Exception as exc:
            raise VaultError("Vault write secret error. Details:"
                             " %s" % exc)

    def read_kv(self, path, mount="kv", version=2):
        try:
            self.logger.info("Reading secret %s/%s", mount, path)
            if version == 2:
                return self._read_kv_2(path, mount)
            return self._read_kv_1(path, mount)
        except Exception as exc:
            raise VaultError("Vault read secret error. Details:"
                             " %s" % exc)

    def _write_kv_1(self, path, mount, **kwargs):
        self._connector.secrets.kv.v1.create_or_update_secret(path=path,
                                                              mount_point=mount,
                                                              secret=kwargs)

    def _write_kv_2(self, path, mount, **kwargs):
        self._connector.secrets.kv.v2.create_or_update_secret(path=path,
                                                              mount_point=mount,
                                                              secret=kwargs)

    def _read_kv_1(self, path, mount):
        return self._connector.secrets.kv.v1.read_secret(path=path, mount_point=mount)

    def _read_kv_2(self, path, mount):
        return self._connector.secrets.kv.v2.read_secret_version(path=path,
                                                                 mount_point=mount)['data']
