from datetime import datetime
from mst_gateway.storage import BaseAsyncStorage


class ThrottleWss(BaseAsyncStorage):
    _duration = 60
    _timeout = None

    async def set(self, key, limit: int, **kwargs) -> None:
        key = self.generate_hash_key(key)
        timeout = kwargs.get("timeout", self._timeout)

        history = await self.get(key)
        history.insert(0, int(limit))
        if self.is_dict:
            self._storage[key] = history
        else:
            await self._storage.set_async(key, history, timeout=timeout)

    async def get(self, key) -> list:
        key = self.generate_hash_key(key)
        if self.is_dict:
            result = self._storage.get(key)
        else:
            result = await self._storage.get_async(key)

        if isinstance(result, list):
            return result
        return []

    async def validate(self, key, rate) -> bool:
        now = int(datetime.utcnow().timestamp())
        if not rate:
            return True
        history = await self.get(key)
        while history and history[-1] <= now - self._duration:
            history.pop()
        if len(history) >= rate:
            return False
        await self.set(key, now)
        return True
