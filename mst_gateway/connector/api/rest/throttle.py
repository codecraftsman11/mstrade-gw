from ..throttle import Throttle


class ThrottleRest(Throttle):

    def set(self, key, limit: int, reset: int, scope: str):
        if self._requests.get(self._key(key)):
            self._requests[self._key(key)].update(
                {
                    scope: [limit, reset]
                }
            )
        else:
            self._requests.update({
                self._key(key): {
                    scope: [limit, reset]
                }
            })

    def get(self, key) -> dict:
        return self._requests.get(self._key(key), {'rest': [0, None]})

    def remove(self, key):
        self._requests.pop(self._key(key), None)
