from ..base import Connector as BaseConnector


DB_FIELDS = ('_handler', '_auth', '_host', '_port',
             '_dbname', '_logger', '_is_closing')


class Connector(BaseConnector):
    # pylint: disable=abstract-method,too-many-arguments,no-self-use

    DEFAULT_PORT = None

    def __init__(self, dbname, host, port, auth, logger=None):
        super().__init__(auth, logger)
        self._dbname = dbname
        self._host = host
        self._port = port or self.__class__.DEFAULT_PORT

    def __getattr__(self, name):
        return getattr(self._handler, name)

    def __setattr__(self, name, value):
        if name in DB_FIELDS:
            self.__dict__[name] = value
            return
        setattr(self._handler, name, value)

    def close(self):
        self._close()

    def _close(self):
        return NotImplementedError
