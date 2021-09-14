from datetime import datetime
from typing import Optional
from .. import DATETIME_FORMAT


def time2timestamp(time: any, msec: bool = True) -> Optional[int]:
    try:
        if isinstance(time, datetime):
            timestamp = time.timestamp()
        elif isinstance(time, str):
            timestamp = datetime.strptime(time.split('Z')[0], DATETIME_FORMAT).timestamp()
        else:
            timestamp = datetime.now().timestamp()
    except (ValueError, TypeError, IndexError):
        return None
    if msec:
        timestamp *= 1000
    return int(timestamp)
