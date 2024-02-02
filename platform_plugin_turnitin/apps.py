"""
platform_plugin_turnitin Django application initialization.
"""

from django.apps import AppConfig

try:
    from openedx.core.constants import COURSE_ID_PATTERN
except ImportError:
    COURSE_ID_PATTERN = object


class PlatformPluginTurnitinConfig(AppConfig):
    """
    Configuration for the platform_plugin_turnitin Django application.
    """

    name = "platform_plugin_turnitin"
    verbose_name = "Platform Plugin Turnitin"

    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "platform-plugin-turnitin",
                "regex": rf"platform-plugin-turnitin/{COURSE_ID_PATTERN}/",
                "relative_path": "urls",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
        "signals_config": {
            "lms.djangoapp": {
                "relative_path": "tasks",
                "receivers": [
                    {
                        "receiver_func_name": "ora_submission_created",
                        "signal_path": "openedx_events.learning.signals.ORA_SUBMISSION_CREATED",
                    },
                ],
            }
        },
    }
