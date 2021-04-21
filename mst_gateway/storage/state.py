from .base import BaseAsyncStorage, BaseSyncStorage


class StateStorage(BaseSyncStorage):
    def set(self, key, value) -> None:
        super().set(key=key, value=value)

    def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = super().get(key=key, exchange=exchange, schema=schema)
        return result


class AsyncStateStorage(BaseAsyncStorage):
    async def set(self, key, value) -> None:
        await super().set(key=key, value=value)

    async def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = await super().get(key=key, exchange=exchange, schema=schema)
        return result
