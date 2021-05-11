from .base import BaseAsyncStorage, BaseSyncStorage


class StateStorage(BaseSyncStorage):

    def get_client(self, write=False):
        if self.is_dict:
            return None
        return self._storage.get_client(key=None, write=write)

    def set(self, key, value, *args, **kwargs) -> None:
        timeout = kwargs.get("timeout", self._timeout)
        _key = self.generate_hash_key(key)
        if self.is_dict:
            _tmp = self._get_dict(_key)
        else:
            _tmp = self._storage.get(_key)
        if isinstance(_tmp, dict) and isinstance(value, dict):
            _tmp.update(value)
        else:
            _tmp = value
        if self.is_dict:
            self._set_dict(_key, _tmp)
        else:
            self._storage.set(_key, _tmp, timeout=timeout)

    def get(self, key, exchange: str = None, schema: str = None, *args, **kwargs) -> dict:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            result = self._get_dict(key) or {}
        else:
            result = self._storage.get(key) or {}
        if exchange:
            result = result.get(exchange.lower(), {})
        if schema:
            result = result.get(schema.lower(), {})
        return result


class AsyncStateStorage(BaseAsyncStorage):

    async def set(self, key, value, *args, **kwargs) -> None:
        timeout = kwargs.get("timeout", self._timeout)
        _key = self.generate_hash_key(key)
        if self.is_dict:
            _tmp = self._get_dict(_key)
        else:
            _tmp = await self._storage.get_async(_key)
        if isinstance(_tmp, dict) and isinstance(_tmp, dict):
            _tmp.update(value)
        else:
            _tmp = value
        if self.is_dict:
            self._set_dict(_key, _tmp)
        else:
            await self._storage.set_async(_key, _tmp, timeout=timeout)

    async def get(self, key, exchange: str = None, schema: str = None, *args, **kwargs) -> dict:
        _key = self.generate_hash_key(key)
        if self.is_dict:
            result = self._get_dict(key) or {}
        else:
            result = await self._storage.get_async(key) or {}
        if exchange:
            result = result.get(exchange.lower(), {})
        if schema:
            result = result.get(schema.lower(), {})
        return result
