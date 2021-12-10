from abc import abstractmethod, ABC
from hashlib import sha1
from typing import Optional


class BaseStorage:
    _timeout = None

    def __init__(self, storage=None, timeout: Optional[int] = None) -> None:
        self._storage = storage or {}
        if isinstance(timeout, int):
            self._timeout = timeout

    @property
    def storage(self):
        return self._storage

    @storage.setter
    def storage(self, _storage):
        self._storage = _storage

    @property
    def is_dict(self) -> bool:
        return isinstance(self._storage, dict)

    @abstractmethod
    def get_client(self, write=False):
        raise NotImplementedError

    @abstractmethod
    def set(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_pattern(self, pattern):
        raise NotImplementedError

    @abstractmethod
    def remove(self, key):
        raise NotImplementedError

    @abstractmethod
    def remove_pattern(self, pattern):
        raise NotImplementedError

    @staticmethod
    def generate_hash_key(key: (str, list, tuple, dict)) -> str:
        if isinstance(key, (list, tuple)):
            return sha1('|'.join(key).encode().lower()).hexdigest()
        if isinstance(key, dict):
            return sha1('|'.join(key.values()).encode().lower()).hexdigest()
        return str(key).lower()

    def _set_dict(self, key: str, value) -> None:
        if isinstance(self._storage.get(key), dict) and isinstance(value, dict):
            self._storage[key].update(value)
        else:
            self._storage[key] = value

    def _get_dict(self, key: str, exchange: str = None, schema: str = None) -> dict:
        result = self._storage.get(key, {})
        if exchange:
            result = result.get(exchange.lower(), {})
        if schema:
            result = result.get(schema.lower(), {})
        return result or None

    def _split_dict_pattern(self, pattern):
        try:
            pattern = pattern.split('*')
            if len(pattern) == 2:
                return pattern[0]
            if len(pattern) == 3:
                return pattern[1]
        except IndexError:
            pass
        return pattern

    def _get_dict_pattern(self, pattern) -> dict:
        result = {}
        pattern = self._split_dict_pattern(pattern)
        for k, v in self._storage.items():
            if pattern in k:
                result[k] = v
        return result

    def _get_dict_keys(self, pattern) -> list:
        result = []
        pattern = self._split_dict_pattern(pattern)
        for k, v in self._storage.items():
            if pattern in k:
                result.append(k)
        return result

    def _remove_dict(self, key: str) -> None:
        self._storage.pop(key, None)

    def _remove_dict_pattern(self, pattern):
        pattern = self._split_dict_pattern(pattern)
        for k, v in self._storage.items():
            if pattern in k:
                self._remove_dict(k)


class BaseSyncStorage(BaseStorage, ABC):

    def get_client(self, write=False):
        if self.is_dict:
            return None
        return self._storage.get_client(key=None, write=write)

    def get_pattern(self, pattern) -> dict:
        if self.is_dict:
            return self._get_dict_pattern(pattern)
        _pattern = self.generate_hash_key(pattern)
        return self._storage.get_pattern(_pattern)

    def get_keys(self, pattern) -> list:
        if self.is_dict:
            return self._get_dict_keys(pattern)
        _pattern = self.generate_hash_key(pattern)
        return self._storage.get_keys(_pattern)

    def remove(self, key) -> None:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            self._remove_dict(_key)
        self._storage.delete(_key)

    def remove_pattern(self, pattern) -> None:
        if self.is_dict:
            return self._remove_dict_pattern(pattern)
        _pattern = self.generate_hash_key(pattern)
        self._storage.delete_pattern(_pattern)


class BaseAsyncStorage(BaseStorage, ABC):

    async def get_client(self, write=False):
        if self.is_dict:
            return None
        return await self._storage.client.get_client(write=write)

    async def get_pattern(self, pattern) -> dict:
        if self.is_dict:
            return self._get_dict_pattern(pattern)
        _pattern = self.generate_hash_key(pattern)
        return await self._storage.get_pattern(_pattern)

    async def get_keys(self, pattern) -> list:
        if self.is_dict:
            return self._get_dict_keys(pattern)
        _pattern = self.generate_hash_key(pattern)
        return await self._storage.keys_async(_pattern)

    async def remove(self, key) -> None:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            self._remove_dict(_key)
        await self._storage.delete_async(_key)

    async def remove_pattern(self, pattern) -> None:
        if self.is_dict:
            return self._remove_dict_pattern(pattern)
        _pattern = self.generate_hash_key(pattern)
        await self._storage.delete_pattern_async(_pattern)
