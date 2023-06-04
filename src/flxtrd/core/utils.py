import datetime
from logging import ERROR

from flxtrd.core.logger import log

MILLI = 1000


def get_formatted_time(milliseconds: int) -> datetime.datetime:
    """
    Converts milliseconds to a human-readable string with milliseconds
    :param milliseconds: milliseconds to convert
    :return: human-readable string with milliseconds
    """

    dt = datetime.datetime.fromtimestamp(milliseconds / MILLI)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def seconds_to_min(seconds: int):
    if seconds == 0:
        log(ERROR, "Duration is zero")
        return 0
    return round(seconds / 60)


def milliseconds_to_min(seconds: int):
    if seconds == 0:
        log(ERROR, "Duration is zero")
        return 0
    return round(seconds / 60 / MILLI)


def utc_timestamp_ms() -> float:
    # Get current UTC timestamp in seconds
    timestamp = datetime.datetime.utcnow().timestamp()
    # Convert seconds to milliseconds
    return int(timestamp * MILLI)


def utc_timestamp_s() -> float:
    # Get current UTC timestamp in seconds
    timestamp = datetime.datetime.utcnow().timestamp()
    return int(timestamp)


def min_to_ms(minutes: int):
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes * 60 * 1000


def min_to_hour(minutes: int):
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes / 60


def min_to_s(minutes: int):
    if minutes == 0:
        log(ERROR, "Minutes can not be zero")
        return 0
    return minutes * 60
