"""Expiration date classification helpers for product batches.

Provides a pure classification function used by services across modules
(inventory, products, purchases, reports). Contains no SQL or Flask
dependencies and never accesses the database.
"""

from datetime import date, datetime, timedelta
from typing import Optional

EXPIRATION_STATUS_EXPIRED = "expired"
EXPIRATION_STATUS_EXPIRING_SOON = "expiring_soon"
EXPIRATION_STATUS_NORMAL = "normal"


def normalize_expiration_date(value: Optional[object]) -> Optional[str]:
    """Normalize a DB expiration value to a YYYY-MM-DD string.

    MySQL DATE columns are returned by the driver as datetime.date or
    datetime.datetime objects, which Flask would serialize as RFC 822
    GMT strings. Normalizing at the repository boundary keeps the API
    consistent with the YYYY-MM-DD contract used by the frontend.

    Args:
        value: A date, datetime, YYYY-MM-DD string, or None.

    Returns:
        YYYY-MM-DD string, or None when value is None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def classify_expiration(
    expiration_date: Optional[object],
    expiring_soon_days: int = 30,
    today: Optional[date] = None,
) -> Optional[str]:
    """Classify a batch expiration date into a status.

    Statuses:
        expired:        expiration date is strictly before today.
        expiring_soon:  expiration date is today or within the configured
                        threshold (inclusive).
        normal:         expiration date is beyond the threshold.
        None:           no expiration date is set.

    Args:
        expiration_date: A date, a YYYY-MM-DD string, or None.
        expiring_soon_days: Number of days from today that counts as
            "expiring soon" (inclusive). Defaults to 30.
        today: Reference date for classification. Defaults to date.today().

    Returns:
        One of the EXPIRATION_STATUS_* constants, or None when no
        expiration date is provided.

    Raises:
        ValueError: If expiration_date is not a valid date or ISO string.
    """
    if expiration_date is None:
        return None

    if isinstance(expiration_date, str):
        expiration_date = date.fromisoformat(expiration_date)

    if not isinstance(expiration_date, date):
        raise ValueError(
            "Expiration date must be a date or a YYYY-MM-DD string"
        )

    reference = today or date.today()

    if expiration_date < reference:
        return EXPIRATION_STATUS_EXPIRED

    if expiration_date <= reference + timedelta(days=expiring_soon_days):
        return EXPIRATION_STATUS_EXPIRING_SOON

    return EXPIRATION_STATUS_NORMAL
