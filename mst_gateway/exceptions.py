import json


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


class RateLimitServiceError(GatewayError):
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


class BinanceAPIException(Exception):

    def __init__(self, response, status_code, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        self.status_code = status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        return 'APIError(code=%s): %s' % (self.code, self.message)


class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message
