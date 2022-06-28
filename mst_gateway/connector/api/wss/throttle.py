from datetime import datetime
from typing import Optional
from mst_gateway.storage import BaseSyncStorage
from mst_gateway.storage.var import StateStorageKey


class ThrottleWss(BaseSyncStorage):
    _duration = 60
    _timeout = None

    def __init__(self, ws_limit: int = 100, storage=None, timeout: Optional[int] = None) -> None:
        self.ws_limit = ws_limit
        super().__init__(storage, timeout)

    def generate_hash_key(self, key: (str, list, tuple, dict)) -> str:
        return f"{StateStorageKey.throttling}:{super().generate_hash_key(key)}"

    def set(self, key, limit: int, **kwargs) -> None:
        key = self.generate_hash_key(key)
        history = self.get(key)
        history.insert(0, int(limit))
        self._storage[key] = history

    def get(self, key) -> list:
        key = self.generate_hash_key(key)
        result = self._storage.get(key)
        if isinstance(result, list):
            return result
        return []

    def validate(self, key, rate) -> bool:
        now = int(datetime.utcnow().timestamp())
        if not rate:
            return True
        history = self.get(key)
        while history and history[-1] <= now - self._duration:
            history.pop()
        if len(history) >= rate:
            return False
        self.set(key, now)
        return True
