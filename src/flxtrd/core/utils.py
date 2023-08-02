from datetime import datetime, timezone
from logging import ERROR

from flxtrd.core.logger import log

MILLI = 1000


def epoch_time_to_isoformat(epoch_time: int) -> datetime:
    """
    Converts milliseconds to a human-readable string with milliseconds
    :param milliseconds: milliseconds to convert
    :return: human-readable date string in iso format
    """
    
    EPOCH_SEC_LENGTH = 10
    milliseconds = "000"

    if not isinstance(epoch_time, str):
        epoch_time = str(epoch_time)

    if len(epoch_time) > EPOCH_SEC_LENGTH:
        milliseconds = epoch_time[EPOCH_SEC_LENGTH:13]
        epoch_time = epoch_time[:EPOCH_SEC_LENGTH]
    elif len(epoch_time) == EPOCH_SEC_LENGTH:
        pass
    else:
        raise ValueError("Epoch time is too short")
    
    dt = datetime.fromtimestamp(int(epoch_time), tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{milliseconds}Z"


def seconds_to_min(seconds: int):
    """Convert seconds to minutes"""
    if seconds == 0:
        log(ERROR, "Duration is zero")
        return 0
    return round(seconds / 60)


def milliseconds_to_min(seconds: int):
    """Convert milliseconds to minutes"""
    if seconds == 0:
        log(ERROR, "Duration is zero")
        return 0
    return round(seconds / 60 / MILLI)


def utc_timestamp_ms() -> float:
    """ Get current UTC timestamp in milliseconds"""
    timestamp = datetime.now(tz=timezone.utc).timestamp()
    # Convert seconds to milliseconds
    return int(timestamp * MILLI)


def utc_timestamp_s() -> float:
    """Get current UTC timestamp in seconds"""
    timestamp = datetime.now(tz=timezone.utc).timestamp()
    return int(timestamp)


def min_to_ms(minutes: int):
    """Convert minutes to milliseconds"""
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes * 60 * 1000


def min_to_hour(minutes: int):
    """Convert minutes to hours"""
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes / 60


def min_to_s(minutes: int):
    """Convert minutes to seconds"""
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes * 60
