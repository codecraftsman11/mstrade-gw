from ..throttle import Throttle


class ThrottleRest(Throttle):

    def set(self, key, limit: int, reset: int, scope: str):
        self._set(self._key(key), {scope: [limit, reset]})

    def get(self, key) -> dict:
        return self._get(self._key(key)) or {'rest': [0, None]}

    def remove(self, key):
        try:
            self._remove(self._key(key))
        except KeyError:
            pass
