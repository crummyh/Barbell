from datetime import datetime, timedelta, timezone

start_time = None


def start_monitor() -> None:
    global start_time
    start_time = datetime.now(timezone.utc)


def get_uptime() -> timedelta:
    """
    Returns the number of seconds since the program started.
    """
    assert start_time
    return datetime.now(timezone.utc) - start_time
