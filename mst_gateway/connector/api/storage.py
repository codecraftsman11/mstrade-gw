from .base import BaseStorage


class StateStorage(BaseStorage):
    timeout = 24 * 60 * 60

    def set(self, key, value: dict):
        self._set(self._key(key), value)

    def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = self._get(self._key(key)) or dict()
        if exchange and schema:
            try:
                return result[exchange.lower()][schema.lower()]
            except KeyError:
                pass
        elif exchange:
            try:
                return result[exchange.lower()]
            except KeyError:
                pass
        return result

    def remove(self, key):
        try:
            self._remove(self._key(key))
        except KeyError:
            pass
