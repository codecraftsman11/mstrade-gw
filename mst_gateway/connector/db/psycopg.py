import random
import string
import psycopg2
from .base import Connector
from ...exceptions import (
    AuthError,
    QueryError,
    ConnectorError,
    IntegrityError
)


def _random_str(count):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(count))  # nosec


class Cursor:
    def __init__(self, _pgsql, **kvargs):
        if not kvargs.get('buffered', True):
            self._cursor = _pgsql.cursor(name="pgsql_{}".format(_random_str(6)))
        else:
            self._cursor = _pgsql.cursor()

    def __getattr__(self, name):
        return getattr(self._cursor, name)

    @property
    def query(self):
        return self._cursor.statement

    def execute(self, *vargs, **kwargs):
        if 'multi' in kwargs:
            kwargs = kwargs.copy()
            del kwargs['multi']
        try:
            return self._cursor.execute(*vargs, **kwargs)
        except psycopg2.IntegrityError as err:
            raise IntegrityError(err.msg, err.errno)
        except psycopg2.Error as err:
            if not err.pgcode \
               or err.pgcode[:2] in ('08',  # Connection Exception
                                     '57',  # Operation Intervention
                                     '58',  # System Error
                                     ''):
                raise err
            raise QueryError(err.pgerror, err.pgcode)


class Psycopg(Connector):
    DEFAULT_PORT = 5432

    def _connect(self, **kwargs):
        try:
            self._handler = psycopg2.connect(dbname=self._dbname, host=self._host,
                                             user=self._auth.user,
                                             password=self._auth.password,
                                             port=self._port, **kwargs)
            self._logger.debug("Psycopg connection to database %s:%s/%s is established",
                               self._host, self._port, self._dbname)
        except AuthError as exc:
            raise AuthError("Invalid credentials connecting postgresql server. Details: "
                            " %s" % exc)
        except psycopg2.Error as exc:
            raise ConnectorError("Can't connect to postgresql server. Details:"
                                 " %s" % exc)
        return self._handler

    def _close(self):
        if self._handler:
            try:
                self._handler.close()
                self._logger.debug("Psycopg connection to database %s is closed",
                                   self._dbname)
            except psycopg2.Error as exc:
                raise ConnectorError(exc)
            finally:
                self._handler = None

    def cursor(self, **kvargs):
        return Cursor(self._handler, **kvargs)


def get_connector_class():
    return Psycopg
