"""
URL module for the Turnitin + Open edX integration.
"""
from django.urls import include, re_path

from platform_plugin_turnitin.api.v1.urls import router

urlpatterns = [
    re_path(r"v1/", include(router.urls)),
]
