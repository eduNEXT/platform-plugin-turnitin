"""
Production Django settings for platform_plugin_turnitin project.
"""

from platform_plugin_turnitin import ROOT_DIRECTORY


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.ENABLE_TURNITIN_SUBMISSION = getattr(settings, "ENV_TOKENS", {}).get(
        "ENABLE_TURNITIN_SUBMISSION", settings.ENABLE_TURNITIN_SUBMISSION
    )
    settings.TURNITIN_TII_API_URL = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_TII_API_URL", settings.TURNITIN_TII_API_URL
    )

    settings.TURNITIN_TCA_INTEGRATION_FAMILY = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_TCA_INTEGRATION_FAMILY", settings.TURNITIN_TCA_INTEGRATION_FAMILY
    )

    settings.TURNITIN_TCA_INTEGRATION_VERSION = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_TCA_INTEGRATION_VERSION", settings.TURNITIN_TCA_INTEGRATION_VERSION
    )

    settings.TURNITIN_TCA_API_KEY = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_TCA_API_KEY", settings.TURNITIN_TCA_API_KEY
    )

    settings.TURNITIN_SIMILARITY_REPORT_PAYLOAD = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_SIMILARITY_REPORT_PAYLOAD",
        settings.TURNITIN_SIMILARITY_REPORT_PAYLOAD,
    )

    settings.TURNITIN_API_TIMEOUT = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_API_TIMEOUT", settings.TURNITIN_API_TIMEOUT
    )
    settings.PLATFORM_PLUGIN_TURNITIN_AUTHENTICATION_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_TURNITIN_AUTHENTICATION_BACKEND",
        settings.PLATFORM_PLUGIN_TURNITIN_AUTHENTICATION_BACKEND,
    )
    settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND",
        settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND,
    )
    settings.PLATFORM_PLUGIN_TURNITIN_COURSE_OVERVIEWS_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_TURNITIN_COURSE_OVERVIEWS_BACKEND",
        settings.PLATFORM_PLUGIN_TURNITIN_COURSE_OVERVIEWS_BACKEND,
    )
    settings.PLATFORM_PLUGIN_TURNITIN_MODULESTORE_BACKEND = getattr(settings, "ENV_TOKENS", {}).get(
        "PLATFORM_PLUGIN_TURNITIN_MODULESTORE_BACKEND",
        settings.PLATFORM_PLUGIN_TURNITIN_MODULESTORE_BACKEND,
    )
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates/turnitin")
