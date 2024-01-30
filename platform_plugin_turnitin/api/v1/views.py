""" Views for the Turnitin API. """
from django.conf import settings
from edx_rest_framework_extensions.auth.session.authentication import (
    SessionAuthenticationAllowInactiveUser,
)
from requests import Response as RequestsResponse
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from platform_plugin_turnitin.api.utils import api_error, get_fullname, validate_request
from platform_plugin_turnitin.edxapp_wrapper import (
    BearerAuthenticationAllowInactiveUser,
)
from platform_plugin_turnitin.models import TurnitinSubmission
from platform_plugin_turnitin.turnitin_client.handlers import (
    get_similarity_report_info,
    get_submission_info,
    post_accept_eula_version,
    post_create_submission,
    post_create_viewer_launch_url,
    put_generate_similarity_report,
    put_upload_submission_file_content,
)
from platform_plugin_turnitin.utils import get_current_datetime


class TurnitinUploadFileAPIView(GenericAPIView):
    """
    Base class for Turnitin API views.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id: str):
        """
        Returns a TurnitinAPI instance.
        """
        turnitin_client = TurnitinClient(request, request.user, course_id)
        agreement_response = turnitin_client.accept_eula_agreement()

        if agreement_response.status_code != status.HTTP_200_OK:
            return api_error(agreement_response.json(), agreement_response.status_code)

        return turnitin_client.upload_turnitin_submission_file()


class TurnitinSubmissionAPIView(GenericAPIView):
    """
    Base class for Turnitin submission API views.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str):
        """
        Returns a TurnitinAPI instance.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.get_submission_status(submission_id)


class TurnitinSimilarityReportAPIView(GenericAPIView):
    """
    Base class for Turnitin similarity report API views.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str):
        """
        Returns a TurnitinAPI instance.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.get_similarity_report_status(submission_id)

    def put(self, request, course_id: str, submission_id: str):
        """
        Returns a TurnitinAPI instance.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.generate_similarity_report(submission_id)


class TurnitinViewerAPIView(GenericAPIView):
    """
    Base class for Turnitin viewer API views.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str):
        """
        Returns a TurnitinAPI instance.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.create_similarity_viewer(submission_id)


class TurnitinClient:
    """Turnitin API client."""

    def __init__(self, request, user, course) -> None:
        self.request = request
        self.user = user
        self.course = course
        self.first_name, self.last_name = get_fullname(self.user.profile.name)

    def accept_eula_agreement(self) -> RequestsResponse:
        """
        Submit acceptance of the EULA for the current user.

        Args:
            user_data (dict): A dictionary containing user data

        Returns:
            RequestsResponse: The response after accepting the EULA.
        """
        payload = {
            "user_id": str(self.user.id),
            "accepted_timestamp": get_current_datetime(),
            "language": "en-US",
        }
        return post_accept_eula_version(payload)

    def upload_turnitin_submission_file(self) -> Response:
        """
        Handle the upload of the user's file to Turnitin.

        Returns:
            Response: The response after uploading the file to Turnitin.
        """
        turnitin_submission = self.create_turnitin_submission_object()

        if turnitin_submission.status_code == status.HTTP_201_CREATED:
            turnitin_submission_id = turnitin_submission.json()["id"]
            submission = TurnitinSubmission(
                user=self.user, turnitin_submission_id=turnitin_submission_id
            )
            submission.save()
            uploaded_file = self.request.FILES["file"]
            return Response(
                put_upload_submission_file_content(
                    turnitin_submission_id, uploaded_file
                ).json()
            )

        return Response(turnitin_submission.json())

    def create_turnitin_submission_object(self) -> RequestsResponse:
        """
        Create a Turnitin submission object based on the user's data.

        Returns:
            RequestsResponse: The response after creating the Turnitin submission object.
        """
        payload = {
            "owner": self.user.id,
            "title": f"{self.course}-{self.user.username}",
            "submitter": self.user.id,
            "owner_default_permission_set": "LEARNER",
            "submitter_default_permission_set": "INSTRUCTOR",
            "extract_text_only": False,
            "metadata": {
                "owners": [
                    {
                        "id": self.user.id,
                        "given_name": self.first_name,
                        "family_name": self.last_name,
                        "email": self.user.email,
                    }
                ],
                "submitter": {
                    "id": self.user.id,
                    "given_name": self.first_name,
                    "family_name": self.last_name,
                    "email": self.user.email,
                },
                "original_submitted_time": get_current_datetime(),
            },
        }
        return post_create_submission(payload)

    def get_submission_status(self, submission_id: str) -> Response:
        """
        Retrieve the status of the latest Turnitin submission for the user.

        Returns:
            Response: Information related to the user's latest Turnitin submission.
        """
        submission = TurnitinSubmission.objects.filter(
            user=self.user, turnitin_submission_id=submission_id
        )
        if not submission:
            return api_error(
                f"Submission with id='{submission_id}' not found.",
                status.HTTP_404_NOT_FOUND,
            )
        return Response(get_submission_info(submission_id).json())

    def generate_similarity_report(self, submission_id: str) -> Response:
        """
        Initialize the generation of a similarity report for the user's latest Turnitin submission.

        Args:
            submission_id (str): The Turnitin submission ID.

        Returns:
            Response: The status of the similarity report generation process.
        """
        submission = TurnitinSubmission.objects.filter(
            user=self.user, turnitin_submission_id=submission_id
        )
        if not submission:
            return api_error(
                f"Submission with id='{submission_id}' not found.",
                status.HTTP_404_NOT_FOUND,
            )
        payload = getattr(settings, "TURNITIN_SIMILARY_REPORT_PAYLOAD", None)
        return Response(put_generate_similarity_report(submission_id, payload).json())

    def get_similarity_report_status(self, submission_id: str) -> Response:
        """
        Retrieve the status of the similarity report for the user's latest Turnitin submission.

        Args:
            submission_id (str): The Turnitin submission ID.

        Returns:
            Response: Information related to the status of the similarity report.
        """
        return Response(get_similarity_report_info(submission_id).json())

    def create_similarity_viewer(self, submission_id: str) -> Response:
        """
        Create a Turnitin similarity viewer for the user's latest submission.

        Args:
            submission_id (str): The Turnitin submission ID.

        Returns:
            Response: Contains the URL for the similarity viewer.
        """
        payload = {
            "viewer_user_id": self.user.id,
            "locale": "en-EN",
            "viewer_default_permission_set": "INSTRUCTOR",
            "viewer_permissions": {
                "may_view_submission_full_source": False,
                "may_view_match_submission_info": False,
                "may_view_document_details_panel": False,
            },
            "similarity": {
                "default_mode": "match_overview",
                "modes": {"match_overview": True, "all_sources": True},
                "view_settings": {"save_changes": True},
            },
            "author_metadata_override": {
                "family_name": self.last_name,
                "given_name": self.first_name,
            },
            "sidebar": {"default_mode": "similarity"},
        }
        return Response(post_create_viewer_launch_url(submission_id, payload).json())
