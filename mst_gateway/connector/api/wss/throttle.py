from datetime import datetime
from ..throttle import Throttle


class ThrottleWss(Throttle):
    duration = 60
    timeout = None

    def set(self, key, limit: int):
        history = self.get(key)
        history.insert(0, int(limit))
        self._set(self._key(key), history)

    def get(self, key) -> list:
        return self._get(self._key(key)) or []

    def remove(self, key):
        try:
            self._remove(self._key(key))
        except KeyError:
            pass

    def validate(self, key, rate):
        now = int(datetime.utcnow().timestamp())
        if not rate:
            return True
        history = self.get(key)
        while history and history[-1] <= now - self.duration:
            history.pop()
        if len(history) >= rate:
            return False

        self.set(key, now)
        return True
