from abc import abstractmethod
from hashlib import sha1


class BaseStorage:
    timeout = None

    def __init__(self, storage=None):
        self._storage = storage or dict()

    @property
    def storage(self):
        return self._storage

    @abstractmethod
    def set(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def remove(self, *args, **kwargs):
        raise NotImplementedError

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
    def _remove(self):
        return self._remove_dict if isinstance(self._storage, dict) else self._remove_cache

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
    def _remove_cache(self):
        return self._storage.delete

    @staticmethod
    def _key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return sha1('|'.join(key).encode()).hexdigest()
        if isinstance(key, dict):
            return sha1('|'.join(key.values()).encode()).hexdigest()
        return str(key).lower()
