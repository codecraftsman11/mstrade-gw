from .base import BaseStorage


class StateStorage(BaseStorage):

    def set(self, key, value: dict):
        self._set(self._key(key), value)

    def get(self, key, exchange: str = None, schema: str = None) -> dict:
        result = self._get(self._key(key)) or dict()
        if exchange and schema:
            try:
                return result[exchange.lower()][schema.lower()]
            except KeyError:
                pass
        elif exchange or schema:
            _key = exchange or schema
            try:
                return result[_key.lower()]
            except KeyError:
                pass
        return result

    def get_pattern(self, key):
        return self._get_pattern(key)

    def remove(self, key):
        try:
            self._remove(self._key(key))
        except KeyError:
            pass

    def remove_pattern(self, key):
        try:
            return self._remove_pattern(key)
        except KeyError:
            pass
