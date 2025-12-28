"""Time helpers.

Python 3.13 deprecates datetime.utcnow().
These helpers provide UTC 'now' without triggering deprecation warnings.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    """Return current UTC time as a naive datetime (tzinfo=None).

    Many of our DB columns are `DateTime` without timezone.
    """

    return datetime.now(timezone.utc).replace(tzinfo=None)


def utcnow_aware() -> datetime:
    """Return current UTC time as a timezone-aware datetime."""

    return datetime.now(timezone.utc)
