"""Utility functions for the Turnitin platform plugin."""

from datetime import datetime

from opaque_keys.edx.keys import UsageKey

from platform_plugin_turnitin.edxapp_wrapper.modulestore import modulestore


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


def enabled_in_course(block_id: str) -> bool:
    """
    Check if Turnitin feature is enabled in the course.

    Args:
        block_id (str): The block ID.

    Returns:
        bool: True if Turnitin feature is enabled in the course, False otherwise.
    """
    course_key = UsageKey.from_string(block_id).course_key
    course_block = modulestore().get_course(course_key)
    return course_block.other_course_settings.get("ENABLE_TURNITIN_SUBMISSION", False)
