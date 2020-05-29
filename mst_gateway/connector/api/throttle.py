from abc import abstractmethod
from hashlib import sha1


class Throttle:
    duration = 60   # in sec

    def __init__(self):
        self._requests = dict()

    @property
    def requests(self):
        return self._requests

    @abstractmethod
    def set(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs) -> dict:
        raise NotImplementedError

    @staticmethod
    def _key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return sha1('|'.join(key).encode()).hexdigest()
        if isinstance(key, dict):
            return sha1('|'.join(key.values()).encode()).hexdigest()
        return str(key).lower()
