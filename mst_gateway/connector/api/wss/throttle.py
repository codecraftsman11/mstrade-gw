from datetime import datetime, timedelta
from ..throttle import Throttle


class ThrottleWss(Throttle):
    duration = 60

    def set(self, key, limit: int):
        now = datetime.utcnow()
        reset = int((now + timedelta(seconds=(self.duration - now.second))).timestamp())
        _limit, _reset = self._requests.get(self._key(key), [limit, reset])
        self._requests[self._key(key)] = [limit, reset] if int(now.timestamp()) > _reset else [_limit + limit, _reset]

    def get(self, key) -> dict:
        return self._requests.get(self._key(key), [0, 0])

    def validate(self, key, rate, limit):
        now = int(datetime.utcnow().timestamp())
        if not rate:
            return True
        connect_count, reset_time = self.get(self._key(key))
        if connect_count >= rate and now < reset_time:
            return False
        self.set(self._key(key), limit)
        return True
