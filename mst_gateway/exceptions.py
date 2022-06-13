class GatewayError(Exception):
    pass


class AuthError(GatewayError):
    pass


class ConfigError(GatewayError):
    pass


class SignalInterrupt(GatewayError):
    pass


class ConnectorError(GatewayError):
    pass


class RecoverableError(GatewayError):
    """ Used for 429 and 5xx status codes. """
    pass


class NotFoundError(GatewayError):
    """ Used for 404 status codes. """
    pass


class QueryError(ConnectorError):
    def __init__(self, msg: str, code: int = None):
        self._code = code
        self._msg = msg
        super().__init__(msg)

    def __str__(self):
        if self._code is not None:
            return f"{self._code}: {self._msg}"
        return self._msg


class IntegrityError(QueryError):
    pass
