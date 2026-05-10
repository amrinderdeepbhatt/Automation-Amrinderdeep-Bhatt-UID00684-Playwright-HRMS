"""Date utility helpers used by tests."""

from datetime import datetime, timedelta


def date_from_offset(offset):
    """Return current datetime shifted by day offset.

    Args:
        offset: Number of days to shift from today.
    """
    return datetime.now() + timedelta(days=offset)
