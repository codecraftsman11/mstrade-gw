class GatewayError(Exception):
    pass


class AuthError(GatewayError):
    pass


class ConfigError(GatewayError):
    pass


class ConnectorError(GatewayError):
    pass


class SignalInterrupt(GatewayError):
    pass
