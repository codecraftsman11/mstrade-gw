from time import time
from typing import Optional
from mst_gateway.storage import BaseSyncStorage, StateStorageKey


class ThrottleRest(BaseSyncStorage):
    _timeout = 60

    def generate_hash_key(self, key: (str, list, tuple, dict)) -> str:
        return f"{StateStorageKey.throttling}:{super().generate_hash_key(key)}"

    def set(self, key, limit: int, reset: int, scope: str, **kwargs) -> None:
        timeout = kwargs.get("timeout", self._timeout)
        key = self.generate_hash_key(key)
        _value = {scope: [limit, reset]}
        if self.is_dict:
            self._set_dict(key, _value)
        else:
            _tmp = self._storage.get(key)
            if isinstance(_tmp, dict):
                _tmp.update(_value)
                self._storage.set(key, _tmp, timeout=timeout)
            else:
                self._storage.set(key, _value, timeout=timeout)

    def get(self, key) -> dict:
        key = self.generate_hash_key(key)
        if self.is_dict:
            result = self._get_dict(key)
        else:
            result = self._storage.get(key)
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
