"""
Settings for the Turnitin plugin.
"""
from platform_plugin_turnitin import ROOT_DIRECTORY


def plugin_settings(settings):
    """
    Read / Update necessary common project settings.
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates/turnitin")
