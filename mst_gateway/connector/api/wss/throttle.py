from datetime import datetime
from mst_gateway.storage import BaseStorage


class ThrottleWss(BaseStorage):
    duration = 60
    timeout = None

    def set(self, key, limit: int):
        history = self.get(key)
        history.insert(0, int(limit))
        self._set(self.generate_hash_key(key), history)

    def get(self, key) -> list:
        if isinstance(_state := self._get(self.generate_hash_key(key)), list):
            return _state
        return []

    def remove(self, key):
        try:
            self._remove(self.generate_hash_key(key))
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
