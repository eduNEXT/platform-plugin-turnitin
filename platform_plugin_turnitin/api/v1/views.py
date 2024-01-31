""" Views for the Turnitin API. """

from django.conf import settings
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from requests import Response as RequestsResponse
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from platform_plugin_turnitin.api.utils import api_error, get_fullname, validate_request
from platform_plugin_turnitin.edxapp_wrapper import BearerAuthenticationAllowInactiveUser
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
    API views providing functionality to upload files for plagiarism checking.

    `Example Requests`:

        * POST platform-plugin-turnitin/{course_id}/api/v1/upload-file

            * Path Parameters:
                * course_id (str): The unique identifier for the course (required).

    `Example Response`:

        * POST platform-plugin-turnitin/{course_id}/api/v1/upload-file

            * 400: The supplied course_id key is not valid.

            * 404: The course is not found.

            * 200: The file was successfully uploaded to Turnitin.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id: str) -> Response:
        """
        Handle the upload of the user's file to Turnitin.
        """
        if response := validate_request(request, course_id, only_course=True):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        agreement_response = turnitin_client.accept_eula_agreement()

        if agreement_response.status_code != status.HTTP_200_OK:
            return api_error(agreement_response.json(), agreement_response.status_code)

        return turnitin_client.upload_turnitin_submission_file()


class TurnitinSubmissionAPIView(GenericAPIView):
    """
    API views providing functionality to retrieve information related to a Turnitin submission.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/submission/{submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * submission_id (str): The unique identifier for the submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/submission/{submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404: The course is not found.

            * 200: The submission information was successfully retrieved.

                The response will contain the following information:

                * owner (str): The username of the user who submitted the file.
                * title (str): The title of the submission.
                * status (str): The status of the submission.
                    Possible values are: CREATED, COMPLETE, PROCESSING, ERROR.
                * id (str): The unique identifier for the submission.
                * content_type (str): The content type of the uploaded file.
                * page_count (int): The number of pages in the uploaded file.
                * word_count (int): The number of words in the uploaded file.
                * character_count (int): The number of characters in the uploaded file.
                * created_time (str): The date and time the submission was created.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str) -> Response:
        """
        Handle the retrieval of the submission information for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.get_submission_status(submission_id)


class TurnitinSimilarityReportAPIView(GenericAPIView):
    """
    API views providing functionality to generate a similarity report for a Turnitin submission.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * submission_id (str): The unique identifier for the submission (required).

        * PUT platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * submission_id (str): The unique identifier for the submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404: The course is not found.

            * 200: The similarity report information was successfully retrieved.

                The response will contain the following information:

                * status (str): The status of the similarity report.
                    Possible values are: COMPLETE, PROCESSING.
                * submission_id (str): The unique identifier for the submission.

        * PUT platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404: The course is not found.

            * 200: The similarity report was successfully generated.

                The response will contain the following information:

                * message (str): The message returned by Turnitin.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str) -> Response:
        """
        Handle the retrieval of the similarity report status for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.get_similarity_report_status(submission_id)

    def put(self, request, course_id: str, submission_id: str) -> Response:
        """
        Handle the generation of a similarity report for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.generate_similarity_report(submission_id)


class TurnitinViewerAPIView(GenericAPIView):
    """
    API views providing functionality to create a Turnitin similarity viewer.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/viewer-url/{submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * submission_id (str): The unique identifier for the submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/viewer-url/{submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404: The course is not found.

            * 200: The similarity viewer was successfully created.

                The response will contain the following information:

                * viewer_url (str): The URL for the similarity viewer.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, submission_id: str) -> Response:
        """
        Handle the creation of a Turnitin similarity viewer.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request, request.user, course_id)
        return turnitin_client.create_similarity_viewer(submission_id)


class TurnitinClient:
    """
    A client class for interacting with Turnitin API.

    Args:
        request: The HTTP request object.
        user: The user object representing the current user.
        course: The course identifier associated with the user.

    Attributes:
        request: The HTTP request object.
        user: The user object representing the current user.
        course: The course identifier associated with the user.
        first_name: The first name of the user extracted from the user profile.
        last_name: The last name of the user extracted from the user profile.

    Methods:
        accept_eula_agreement():
            Submit acceptance of the End-User License Agreement (EULA) for the current user.
        upload_turnitin_submission_file():
            Handle the upload of the user's file to Turnitin.
        create_turnitin_submission_object():
            Create a Turnitin submission object based on the user's data.
        get_submission_status(submission_id: str):
            Retrieve the status of the latest Turnitin submission for the user.
        generate_similarity_report(submission_id: str):
            Initialize the generation of a similarity report for the user's latest Turnitin submission.
        get_similarity_report_status(submission_id: str):
            Retrieve the status of the similarity report for the user's latest Turnitin submission.
        create_similarity_viewer(submission_id: str):
            Create a Turnitin similarity viewer for the user's latest submission.
    """

    def __init__(self, request, user, course) -> None:
        self.request = request
        self.user = user
        self.course = course
        self.first_name, self.last_name = get_fullname(self.user.profile.name)

    def accept_eula_agreement(self) -> RequestsResponse:
        """
        Submit acceptance of the EULA for the current user.

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
