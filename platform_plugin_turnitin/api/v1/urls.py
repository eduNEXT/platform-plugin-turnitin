"""URL patterns for the Turnitin API"""

from django.urls import path

from platform_plugin_turnitin.api.v1 import views

app_name = "platform_plugin_turnitin"

urlpatterns = [
    path(
        "upload-file/<uuid:ora_submission_id>/",
        views.TurnitinUploadFileAPIView.as_view(),
        name="upload-file",
    ),
    path(
        "submission/<uuid:ora_submission_id>/",
        views.TurnitinSubmissionAPIView.as_view(),
        name="get-submission",
    ),
    path(
        "similarity-report/<uuid:ora_submission_id>/",
        views.TurnitinSimilarityReportAPIView.as_view(),
        name="generate-similarity-report",
    ),
    path(
        "similarity-report/<uuid:ora_submission_id>/",
        views.TurnitinSimilarityReportAPIView.as_view(),
        name="get-similarity-report",
    ),
    path(
        "viewer-url/<uuid:ora_submission_id>/",
        views.TurnitinViewerAPIView.as_view(),
        name="viewer-url",
    ),
]
