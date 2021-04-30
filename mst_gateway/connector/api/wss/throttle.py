from datetime import datetime
from mst_gateway.storage import BaseAsyncStorage


class ThrottleWss(BaseAsyncStorage):
    _duration = 60
    _timeout = None

    async def set(self, key, limit: int) -> None:
        await super().set(key=key, value=limit)

    async def get(self, key) -> list:
        if isinstance(_state := await super().get(key), list):
            return _state
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
