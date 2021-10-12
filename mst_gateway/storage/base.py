from abc import abstractmethod, ABC
from hashlib import sha1
from typing import Optional
from mst_gateway.storage.var import StateStorageKey


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
            return f"{StateStorageKey.throttling}:{sha1('|'.join(key).encode().lower()).hexdigest()}"
        if isinstance(key, dict):
            return f"{StateStorageKey.throttling}:{sha1('|'.join(key.values()).encode().lower()).hexdigest()}"
        return f"{StateStorageKey.throttling}:{str(key).lower()}"

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

    def _remove_dict(self, key: str) -> None:
        self._storage.pop(key, None)


class BaseSyncStorage(BaseStorage, ABC):

    def get_client(self, write=False):
        if self.is_dict:
            return None
        return self._storage.get_client(key=None, write=write)

    def get_pattern(self, pattern) -> dict:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            return self._get_dict(_pattern)
        return self._storage.get_pattern(_pattern)

    def get_keys(self, pattern) -> list:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            if _pattern in self._storage:
                return [_pattern]
            return []
        return self._storage.get_keys(_pattern)

    def remove(self, key) -> None:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            self._remove_dict(_key)
        self._storage.delete(_key)

    def remove_pattern(self, pattern) -> None:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            self._remove_dict(_pattern)
        self._storage.delete_pattern(_pattern)


class BaseAsyncStorage(BaseStorage, ABC):

    async def get_client(self, write=False):
        if self.is_dict:
            return None
        return await self._storage.client.get_client(write=write)

    async def get_pattern(self, pattern) -> dict:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            return self._get_dict(_pattern)
        return await self._storage.get_pattern(_pattern)

    async def get_keys(self, pattern) -> list:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            if _pattern in self._storage:
                return [_pattern]
            return []
        return await self._storage.keys_async(_pattern)

    async def remove(self, key) -> None:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            self._remove_dict(_key)
        await self._storage.delete_async(_key)

    async def remove_pattern(self, pattern) -> None:
        _pattern = self.generate_hash_key(pattern)
        if self.is_dict:
            self._remove_dict(_pattern)
        await self._storage.delete_pattern_async(_pattern)
