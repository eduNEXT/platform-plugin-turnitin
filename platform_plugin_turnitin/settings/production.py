"""
Production Django settings for platform_plugin_turnitin project.
"""


def plugin_settings(settings):  # pylint: disable=unused-argument
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
