from abc import abstractmethod
from typing import Optional
from hashlib import sha1


class BaseStorage:
    timeout = None

    def __init__(self, storage=None, timeout: Optional[int] = None):
        self._storage = storage or dict()
        if isinstance(timeout, int):
            self.timeout = timeout

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, _storage):
        self._storage = _storage

    @abstractmethod
    def set(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_pattern(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove(self, *args, **kwargs):
        raise NotImplementedError

    def get_keys(self, key):
        if isinstance(self._storage, dict):
            return [key] if key in self._storage else list()
        return self._get_cache_keys(key)

    def _set(self, key: str, data):
        if isinstance(self._storage, dict):
            if isinstance(self._get_dict(key), dict):
                self._add_dict[key].update(data)
            else:
                self._add_dict[key] = data
        else:
            _tmp = self._get_cache(key, None)
            if isinstance(_tmp, dict):
                _tmp.update(data)
                self._set_cache(key, _tmp, timeout=self.timeout)
            else:
                self._set_cache(key, data, timeout=self.timeout)

    @property
    def _get(self):
        return self._get_dict if isinstance(self._storage, dict) else self._get_cache

    @property
    def _get_pattern(self):
        return self._get_dict if isinstance(self._storage, dict) else self._get_cache_pattern

    @property
    def _remove(self):
        return self._remove_dict if isinstance(self._storage, dict) else self._remove_cache

    @property
    def _remove_pattern(self):
        return self._remove_dict if isinstance(self._storage, dict) else self._remove_cache_pattern

    @property
    def _set_dict(self):
        return self._storage.update

    @property
    def _add_dict(self):
        return self._storage

    @property
    def _get_dict(self):
        return self._storage.get

    @property
    def _remove_dict(self):
        return self._storage.pop

    @property
    def _set_cache(self):
        return self._storage.set

    @property
    def _add_cache(self):
        return self._storage.add

    @property
    def _get_cache(self):
        return self._storage.get

    @property
    def _get_cache_pattern(self):
        return self._storage.get_pattern

    @property
    def _get_cache_keys(self):
        return self._storage.get_keys

    @property
    def _remove_cache_pattern(self):
        return self._storage.delete_pattern

    @property
    def _remove_cache(self):
        return self._storage.delete

    @staticmethod
    def generate_hash_key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return sha1('|'.join(key).encode().lower()).hexdigest()
        if isinstance(key, dict):
            return sha1('|'.join(key.values()).encode().lower()).hexdigest()
        return str(key).lower()
