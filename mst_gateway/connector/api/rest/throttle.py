from mst_gateway.storage import BaseStorage


class ThrottleRest(BaseStorage):
    timeout = 60

    def set(self, key, limit: int, reset: int, scope: str):
        self._set(self.generate_hash_key(key), {scope: [limit, reset]})

    def get(self, key) -> dict:
        return self._get(self.generate_hash_key(key)) or {'rest': [0, None]}

    def remove(self, key):
        try:
            self._remove(self.generate_hash_key(key))
        except KeyError:
            pass
