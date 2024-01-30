"""
Production Django settings for platform_plugin_turnitin project.
"""


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
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

    settings.TURNITIN_SIMILARY_REPORT_PAYLOAD = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_SIMILARY_REPORT_PAYLOAD", settings.TURNITIN_SIMILARY_REPORT_PAYLOAD
    )

    settings.TURNITIN_API_TIMEOUT = getattr(settings, "ENV_TOKENS", {}).get(
        "TURNITIN_API_TIMEOUT", settings.TURNITIN_API_TIMEOUT
    )
