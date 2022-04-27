from time import time
from typing import Optional
from mst_gateway.storage import BaseSyncStorage, StateStorageKey


class ThrottleRest(BaseSyncStorage):
    _timeout = 60

    def __init__(self, rest_limit: int = 100, order_limit: int = 10, storage=None, timeout: Optional[int] = None) -> None:
        self.rest_limit = rest_limit
        self.order_limit = order_limit
        super(ThrottleRest, self).__init__(storage, timeout)

    def generate_hash_key(self, key: (str, list, tuple, dict)) -> str:
        return f"{StateStorageKey.throttling}:{super().generate_hash_key(key)}"

    def set(self, key, limit: int, reset: int, scope: str, **kwargs) -> None:
        key = self.generate_hash_key(key)
        _value = {scope: [limit, reset]}
        self._set_dict(key, _value)

    def get(self, key) -> dict:
        key = self.generate_hash_key(key)
        result = self._get_dict(key)
        if isinstance(result, dict):
            return result
        return {'rest': [0, None]}

    def validate(self, key, throttle_limit) -> Optional[int]:
        if not throttle_limit:
            return
        throttling_data = self.get(key).get('rest', [])
        try:
            request_count, reset_time = throttling_data[0], throttling_data[1]
        except IndexError:
            request_count = 0
            reset_time = 0
        if request_count >= throttle_limit and reset_time > float(time()):
            return reset_time
        return None
