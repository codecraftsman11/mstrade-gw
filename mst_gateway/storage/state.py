from .base import BaseAsyncStorage, BaseSyncStorage


class StateStorage(BaseSyncStorage):
    def set(self, key, value, timeout=None) -> None:
        super().set(key=key, value=value, timeout=timeout)

    def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = super().get(key=key, exchange=exchange, schema=schema)
        return result


class AsyncStateStorage(BaseAsyncStorage):
    async def set(self, key, value, timeout=None) -> None:
        await super().set(key=key, value=value, timeout=timeout)

    async def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = await super().get(key=key, exchange=exchange, schema=schema)
        return result
