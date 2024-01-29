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
    }

    def ready(self) -> None:
        """
        Perform application initialization once the Django platform has been initialized.
        """
        super().ready()
        from platform_plugin_turnitin.turnitin import (  # no-qa pylint: disable=import-outside-toplevel,unused-import
            TurnitinXBlock,
        )
