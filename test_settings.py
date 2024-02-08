"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "platform_plugin_turnitin",
)

LOCALE_PATHS = [
    root("platform_plugin_turnitin", "conf", "locale"),
]

ROOT_URLCONF = "platform_plugin_turnitin.urls"

SECRET_KEY = "insecure-secret-key"

MIDDLEWARE = (
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",  # this is required for admin
                "django.contrib.messages.context_processors.messages",  # this is required for admin
            ],
        },
    }
]

# Plugin settings
PLATFORM_PLUGIN_TURNITIN_AUTHENTICATION_BACKEND = (
    "platform_plugin_turnitin.edxapp_wrapper.backends.authentication_q_v1_test"
)
PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND = (
    "platform_plugin_turnitin.edxapp_wrapper.backends.student_q_v1_test"
)
PLATFORM_PLUGIN_TURNITIN_COURSE_OVERVIEWS_BACKEND = (
    "platform_plugin_turnitin.edxapp_wrapper.backends.course_overviews_q_v1_test"
)
TURNITIN_SIMILARITY_REPORT_PAYLOAD = {"test_key": "test_value"}
