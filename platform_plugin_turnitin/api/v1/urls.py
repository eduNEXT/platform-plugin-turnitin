"""
Router module for the Turnitin + Open edX integration API.
"""
from rest_framework.routers import DefaultRouter

from platform_plugin_turnitin.api.v1.views import PlagiarismView

router = DefaultRouter()
router.register(r"plagiarism", PlagiarismView, basename="plagiarism")
