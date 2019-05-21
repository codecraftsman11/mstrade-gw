import signal
from .exceptions import SignalInterrupt


class SignalHandler:
    SIGNALS = ('SIGINT', 'SIGTERM')

    def __init__(self):
        for sig in self.__class__.SIGNALS:
            signal.signal(getattr(signal, sig), self._raise)

    def _raise(self, signum, frame):
        # pylint: disable=no-self-use,unused-argument
        raise SignalInterrupt(signum)
