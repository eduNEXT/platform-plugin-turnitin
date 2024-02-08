""" URL patterns for the Turnitin API."""

from django.urls import include, path

app_name = "platform_plugin_turnitin"

urlpatterns = [
    path(
        "v1/",
        include("platform_plugin_turnitin.api.v1.urls", namespace="v1"),
    ),
]
