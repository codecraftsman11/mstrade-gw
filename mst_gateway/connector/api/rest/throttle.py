from typing import List


class Throttle:
    _requests = dict()

    @property
    def requests(self):
        return self._requests

    @classmethod
    def set(cls, key, limit: int, reset: int):
        cls._requests.update({
            cls._key(key): [limit, reset]
        })

    @classmethod
    def get(cls, key) -> List[int]:
        return cls._requests.get(cls._key(key), [0, None])

    @classmethod
    def remove(cls, key):
        cls._requests.pop(cls._key(key), None)

    @staticmethod
    def _key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return '|'.join(key)
        if isinstance(key, dict):
            return '|'.join(key.values())
        return str(key).lower()
