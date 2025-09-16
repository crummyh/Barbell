from datetime import datetime, timezone

start_time = None


def start_monitor():
    global start_time
    start_time = datetime.now(timezone.utc)


def get_uptime():
    """
    Returns the number of seconds since the program started.
    """
    assert start_time
    return datetime.now(timezone.utc) - start_time
