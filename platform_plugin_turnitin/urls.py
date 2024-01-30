"""URL patterns for the platform_plugin_turnitin plugin."""

from django.urls import include, path

app_name = "platform_plugin_turnitin"

urlpatterns = [
    path(
        "api/",
        include(
            "platform_plugin_turnitin.api.urls",
            namespace="turnitin-api",
        ),
    ),
]
