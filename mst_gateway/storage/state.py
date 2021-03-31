from .base import BaseAsyncStorage, BaseSyncStorage


class StateStorage(BaseSyncStorage):

    def set(self, key, value) -> None:
        super().set(key=key, value=value)

    def get(self, key, exchange: str = None, schema: str = None) -> dict:
        return super().get(key=key, exchange=exchange, schema=schema)


class AsyncStateStorage(BaseAsyncStorage):

    async def set(self, key, value) -> None:
        await super().set(key=key, value=value)

    async def get(self, key, exchange: str = None, schema: str = None) -> dict:
        return await super(AsyncStateStorage, self).get(key=key, exchange=exchange, schema=schema)
