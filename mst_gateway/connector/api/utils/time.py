from datetime import datetime
from .. import DATETIME_FORMAT


def time2timestamp(time: any, msec: bool = True) -> int:
    if isinstance(time, datetime):
        timestamp = time.timestamp()
    elif isinstance(time, str):
        timestamp = datetime.strptime(time, DATETIME_FORMAT).timestamp()
    else:
        timestamp = datetime.now().timestamp()
    if msec:
        timestamp *= 1000
    return int(timestamp)
