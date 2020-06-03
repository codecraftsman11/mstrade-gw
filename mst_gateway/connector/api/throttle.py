from abc import abstractmethod
from hashlib import sha1


class Throttle:
    duration = 60   # in sec
    timeout = 60    # in sec

    def __init__(self, storage=None):
        self._requests = storage or dict()

    @property
    def requests(self):
        return self._requests

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
        if isinstance(self._requests, dict):
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
        return self._get_dict if isinstance(self._requests, dict) else self._get_cache

    @property
    def _remove(self):
        return self._remove_dict if isinstance(self._requests, dict) else self._remove_cache

    @property
    def _set_dict(self):
        return self._requests.update

    @property
    def _add_dict(self):
        return self._requests

    @property
    def _get_dict(self):
        return self._requests.get

    @property
    def _remove_dict(self):
        return self._requests.pop

    @property
    def _set_cache(self):
        return self._requests.set

    @property
    def _add_cache(self):
        return self._requests.add

    @property
    def _get_cache(self):
        return self._requests.get

    @property
    def _remove_cache(self):
        return self._requests.delete

    @staticmethod
    def _key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return sha1('|'.join(key).encode()).hexdigest()
        if isinstance(key, dict):
            return sha1('|'.join(key.values()).encode()).hexdigest()
        return str(key).lower()
