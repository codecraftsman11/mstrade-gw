from mst_gateway.storage import BaseSyncStorage, StateStorageKey


class ThrottleRest(BaseSyncStorage):
    _timeout = 60

    def generate_hash_key(self, key: (str, list, tuple, dict)) -> str:
        return f'{StateStorageKey.throttling}:{super(ThrottleRest, self).generate_hash_key(key)}'

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

