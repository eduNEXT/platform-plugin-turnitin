"""
Common Django settings for the platform_plugin_turnitin project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""
from platform_plugin_turnitin import ROOT_DIRECTORY

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.22/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "secret-key"


# Application definition

INSTALLED_APPS = [
    "platform_plugin_turnitin",
]


# Internationalization
# https://docs.djangoproject.com/en/2.22/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """

    # Configuration variables
    settings.TURNITIN_TII_API_URL = None
    settings.TURNITIN_TCA_INTEGRATION_FAMILY = None
    settings.TURNITIN_TCA_INTEGRATION_VERSION = None
    settings.TURNITIN_TCA_API_KEY = None
    settings.TURNITIN_SIMILARY_REPORT_PAYLOAD = {
        "indexing_settings": {"add_to_index": True},
        "generation_settings": {
            "search_repositories": [
                "INTERNET",
                "SUBMITTED_WORK",
                "PUBLICATION",
                "CROSSREF",
                "CROSSREF_POSTED_CONTENT",
            ],
            "submission_auto_excludes": [],
            "auto_exclude_self_matching_scope": "ALL",
            "priority": "HIGH",
        },
        "view_settings": {
            "exclude_quotes": True,
            "exclude_bibliography": True,
            "exclude_citations": False,
            "exclude_abstract": False,
            "exclude_methods": False,
            "exclude_custom_sections": False,
            "exclude_preprints": False,
            "exclude_small_matches": 8,
            "exclude_internet": False,
            "exclude_publications": False,
            "exclude_crossref": False,
            "exclude_crossref_posted_content": False,
            "exclude_submitted_works": False,
        },
    }
    settings.TURNITIN_API_TIMEOUT = 30
    settings.PLATFORM_PLUGIN_TURNITIN_AUTHENTICATION_BACKEND = (
        "platform_plugin_turnitin.edxapp_wrapper.backends.authentication_q_v1"
    )
    settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND = (
        "platform_plugin_turnitin.edxapp_wrapper.backends.student_q_v1"
    )
    settings.PLATFORM_PLUGIN_TURNITIN_COURSE_OVERVIEWS_BACKEND = (
        "platform_plugin_turnitin.edxapp_wrapper.backends.course_overviews_q_v1"
    )
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates/turnitin")
