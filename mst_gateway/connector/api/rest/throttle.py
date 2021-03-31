from mst_gateway.storage import BaseSyncStorage


class ThrottleRest(BaseSyncStorage):
    _timeout = 60

    def set(self, key, limit: int, reset: int, scope: str):
        super().set(key=key, value={scope: [limit, reset]})

    def get(self, key) -> dict:
        return super().get(key=key) or {'rest': [0, None]}
