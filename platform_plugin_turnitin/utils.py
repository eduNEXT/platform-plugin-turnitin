"""Utility functions for the Turnitin platform plugin."""

from datetime import datetime


def get_current_datetime() -> str:
    """
    Return the current datetime in ISO 8601 format.

    Example:
        >>> get_current_datetime()
        '2024-01-01T12:00:00Z'

    Returns:
        str: The current datetime in ISO 8601 format.
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
