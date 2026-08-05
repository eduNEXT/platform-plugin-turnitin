"""Utility functions for the Turnitin platform plugin."""

from datetime import datetime, timezone

from django.utils import translation
from opaque_keys.edx.keys import UsageKey
from requests.exceptions import RequestException

from platform_plugin_turnitin.constants import ALLOWED_FILE_EXTENSIONS
from platform_plugin_turnitin.edxapp_wrapper.modulestore import modulestore
from platform_plugin_turnitin.turnitin_client.handlers import get_eula_version_info


def get_current_datetime() -> str:
    """
    Return the current datetime in ISO 8601 format.

    Example:
        >>> get_current_datetime()
        '2024-01-01T12:00:00Z'

    Returns:
        str: The current datetime in ISO 8601 format.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_allowed_file_extension(filename: str) -> bool:
    """
    Check whether a filename's extension is one Turnitin is allowed to receive.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the file's extension is in ALLOWED_FILE_EXTENSIONS, False otherwise.
    """
    return filename.split(".")[-1] in ALLOWED_FILE_EXTENSIONS


def get_turnitin_locale() -> str:
    """
    Map the active Django language to a Turnitin-accepted locale string.

    Reflects the requesting user's language on the direct REST endpoints, where Django's
    locale middleware has already activated it for the request. Celery tasks have no active
    request, so this falls back to the deployment's default ``LANGUAGE_CODE`` there — still an
    improvement over a hardcoded locale on Spanish-only deployments.

    Returns:
        str: ``"es-ES"`` for any Spanish variant, ``"en-US"`` otherwise.
    """
    language = translation.get_language() or ""
    if language.split("-")[0].lower() == "es":
        return "es-ES"
    return "en-US"


def resolve_current_eula_version() -> str:
    """
    Resolve Turnitin's current EULA version via `GET /eula/latest`.

    Falls back to `"v1beta"` (the previous hardcoded value) if the lookup fails, so a transient
    issue here doesn't block EULA display or acceptance outright.

    The response is assumed to carry the version identifier under a top-level `"version"` key —
    this isn't confirmed against Turnitin's documented response schema, only inferred from the
    documented `GET /eula/latest` best-practice workflow.

    Returns:
        str: The current EULA version identifier.
    """
    try:
        response = get_eula_version_info()
    except RequestException:
        return "v1beta"

    if response.ok:
        try:
            return response.json()["version"]
        except (ValueError, KeyError):
            pass

    return "v1beta"


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
