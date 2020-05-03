from mysql.connector import connect, Error
from .base import Connector
from ...exceptions import AuthError, ConnectorError, QueryError


class Cursor:
    def __init__(self, _mysql, **kwargs):
        self._cursor = None
        self._deferred_err = None
        try:
            self._cursor = _mysql.cursor(buffered=kwargs.pop('buffered', True), **kwargs)
        except Error as err:
            self._deferred_err = err

    def __getattr__(self, name):
        if self._cursor is None:
            raise self._deferred_err
        return getattr(self._cursor, name)

    @property
    def query(self):
        if self._cursor is None:
            raise self._deferred_err
        return self._cursor.statement

    def execute(self, *vargs, **kwargs):
        if self._cursor is None:
            raise self._deferred_err
        try:
            res = self._cursor.execute(*vargs, **kwargs)
            if kwargs.get('multi'):
                res = list(res)
            return res
        except Error as err:
            if err.errno < 1000 \
               or 2000 <= err.errno < 3000:
                raise err
            raise QueryError(err.msg, err.errno)


class MySQL(Connector):
    DEFAULT_PORT = 3306

    def _connect(self, **kwargs):
        try:
            self._handler = connect(database=self._dbname, host=self._host,
                                    user=self._auth.user,
                                    password=self._auth.password,
                                    port=self._port, **kwargs)
            self._logger.debug("MySQL connection to database %s:%s/%s is established",
                               self._host, self._port, self._dbname)
        except AuthError as exc:
            raise AuthError("Invalid credentials connecting mysql server. Details: "
                            " %s" % exc)
        except Error as exc:
            raise ConnectorError("Can't connect to mysql server. Details:"
                                 " %s" % exc)
        return self._handler

    def _close(self):
        if self._handler:
            try:
                self._handler.close()
                self._logger.debug("MySQL connection to database %s is closed",
                                   self._dbname)
            except Error as exc:
                raise ConnectorError(exc)
            finally:
                self._handler = None

    def cursor(self, **kwargs):
        return Cursor(self._handler, **kwargs)


def get_connector_class():
    return MySQL
