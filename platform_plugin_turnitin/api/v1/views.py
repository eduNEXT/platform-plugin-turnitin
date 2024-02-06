""" Views for the Turnitin API. """

from __future__ import annotations

from django.conf import settings
from django.db.models.query import QuerySet
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

        * POST platform-plugin-turnitin/{course_id}/api/v1/upload-file/{ora_submission_id}

            * Path Parameters:
                * course_id (str): The unique identifier for the course (required).
                * ora_submission_id (str): The unique identifier for the ora submission (required).

    `Example Response`:

        * POST platform-plugin-turnitin/{course_id}/api/v1/upload-file/{ora_submission_id}

            * 400: The supplied course_id key is not valid.

            * 404: The course is not found.

            * 200: The file was successfully uploaded to Turnitin.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, course_id: str, ora_submission_id: str) -> Response:
        """
        Handle the upload of the user's file to Turnitin.
        """
        if response := validate_request(request, course_id, only_course=True):
            return response

        turnitin_client = TurnitinClient(request.user, request.FILES.get("file"))
        agreement_response = turnitin_client.accept_eula_agreement()

        if agreement_response.status_code != status.HTTP_200_OK:
            return api_error(agreement_response.json(), agreement_response.status_code)

        return turnitin_client.upload_turnitin_submission_file(ora_submission_id)


class TurnitinSubmissionAPIView(GenericAPIView):
    """
    API views providing functionality to retrieve information related to a Turnitin submission.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/submission/{ora_submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * ora_submission_id (str): The unique identifier for the ora submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/submission/{ora_submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404:
                * The course is not found.
                * The ORA submission is not found.

            * 200: The submission information was successfully retrieved.

                The response will contain a list with the following information:

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

    def get(self, request, course_id: str, ora_submission_id: str) -> Response:
        """
        Handle the retrieval of the submission information for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request.user)
        return turnitin_client.get_submission_status(ora_submission_id)


class TurnitinSimilarityReportAPIView(GenericAPIView):
    """
    API views providing functionality to generate a similarity report for a Turnitin submission.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{ora_submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * ora_submission_id (str): The unique identifier for the ora submission (required).

        * PUT platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{ora_submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * ora_submission_id (str): The unique identifier for the ora submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{ora_submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404:
                * The course is not found.
                * The ORA submission is not found.

            * 200: The similarity report information was successfully retrieved.

                The response will contain a list with the following information:

                * status (str): The status of the similarity report.
                    Possible values are: COMPLETE, PROCESSING.
                * submission_id (str): The unique identifier for the submission.

        * PUT platform-plugin-turnitin/{course_id}/api/v1/similarity-report/{ora_submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404:
                * The course is not found.
                * The ORA submission is not found.

            * 200: The similarity report was successfully generated.

                The response will contain a list with the following information:

                * message (str): The message returned by Turnitin.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, ora_submission_id: str) -> Response:
        """
        Handle the retrieval of the similarity report status for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request.user)
        return turnitin_client.get_similarity_report_status(ora_submission_id)

    def put(self, request, course_id: str, ora_submission_id: str) -> Response:
        """
        Handle the generation of a similarity report for a Turnitin submission.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request.user)
        return turnitin_client.generate_similarity_report(ora_submission_id)


class TurnitinViewerAPIView(GenericAPIView):
    """
    API views providing functionality to create a Turnitin similarity viewer.

    `Example Requests`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/viewer-url/{ora_submission_id}

            * Path Parameters:

                * course_id (str): The unique identifier for the course (required).
                * ora_submission_id (str): The unique identifier for the ora submission (required).

    `Example Response`:

        * GET platform-plugin-turnitin/{course_id}/api/v1/viewer-url/{ora_submission_id}

            * 400: The supplied course_id key is not valid.

            * 403: The user does not have permission to access the submission.

            * 404:
                * The course is not found.
                * The ORA submission is not found.

            * 200: The similarity viewer was successfully created.

                The response will contain a list with the following information:

                * viewer_url (str): The URL for the similarity viewer.
    """

    authentication_classes = (
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str, ora_submission_id: str) -> Response:
        """
        Handle the creation of a Turnitin similarity viewer.
        """
        if response := validate_request(request, course_id):
            return response

        turnitin_client = TurnitinClient(request.user)
        return turnitin_client.create_similarity_viewer(ora_submission_id)


class TurnitinClient:
    """
    A client class for interacting with Turnitin API.

    Args:
        user: The user object representing the current user.
        file: The file to be uploaded to Turnitin (optional).

    Attributes:
        user: The user object representing the current user.
        file: The file to be uploaded to Turnitin.
        first_name: The first name of the user extracted from the user profile.
        last_name: The last name of the user extracted from the user profile.

    Methods:
        accept_eula_agreement():
            Submit acceptance of the End-User License Agreement (EULA) for the current user.
        upload_turnitin_submission_file(ora_submission_id: str):
            Handle the upload of the user's file to Turnitin.
        create_turnitin_submission_object():
            Create a Turnitin submission object based on the user's data.
        get_submission_status(ora_submission_id: str):
            Retrieve the status of the latest Turnitin submission for the user.
        generate_similarity_report(ora_submission_id: str):
            Initialize the generation of a similarity report for the user's latest Turnitin submission.
        get_similarity_report_status(ora_submission_id: str):
            Retrieve the status of the similarity report for the user's latest Turnitin submission.
        create_similarity_viewer(ora_submission_id: str):
            Create a Turnitin similarity viewer for the user's latest submission.
    """

    def __init__(self, user, file=None) -> None:
        self.user = user
        self.file = file
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

    def upload_turnitin_submission_file(self, ora_submission_id: str) -> Response:
        """
        Handle the upload of the user's file to Turnitin.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            Response: The response after uploading the file to Turnitin.
        """
        turnitin_submission = self.create_turnitin_submission_object()

        if turnitin_submission.status_code == status.HTTP_201_CREATED:
            turnitin_submission_id = turnitin_submission.json()["id"]
            submission = TurnitinSubmission(
                user=self.user,
                ora_submission_id=ora_submission_id,
                turnitin_submission_id=turnitin_submission_id,
            )
            submission.save()
            return Response(
                put_upload_submission_file_content(
                    turnitin_submission_id, self.file
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
            "title": f"{self.file.name}-{self.user.username}",
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

    def get_submission_status(self, ora_submission_id: str) -> Response:
        """
        Retrieve the status of the latest Turnitin submission for the user.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            Response: Information related to the user's latest Turnitin submission.
        """
        submissions = self.get_submissions(ora_submission_id)
        if isinstance(submissions, Response):
            return submissions

        response_list = []
        for submission in submissions:
            response = get_submission_info(submission.turnitin_submission_id)
            response_list.append(response.json())

        return Response(response_list)

    def generate_similarity_report(self, ora_submission_id: str) -> Response:
        """
        Initialize the generation of a similarity report for the user's latest Turnitin submission.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            Response: The status of the similarity report generation process.
        """
        submissions = self.get_submissions(ora_submission_id)
        if isinstance(submissions, Response):
            return submissions

        payload = getattr(settings, "TURNITIN_SIMILARY_REPORT_PAYLOAD", None)
        response_list = []
        for submission in submissions:
            response = put_generate_similarity_report(
                submission.turnitin_submission_id, payload
            )
            response_list.append(response.json())

        return Response(response_list)

    def get_similarity_report_status(self, ora_submission_id: str) -> Response:
        """
        Retrieve the status of the similarity report for the user's latest Turnitin submission.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            Response: Information related to the status of the similarity report.
        """
        submissions = self.get_submissions(ora_submission_id)
        if isinstance(submissions, Response):
            return submissions

        response_list = []
        for submission in submissions:
            response = get_similarity_report_info(submission.turnitin_submission_id)
            response_list.append(response.json())

        return Response(response_list)

    def create_similarity_viewer(self, ora_submission_id: str) -> Response:
        """
        Create a Turnitin similarity viewer for the user's latest submission.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            Response: Contains the URL for the similarity viewer.
        """
        submissions = self.get_submissions(ora_submission_id)
        if isinstance(submissions, Response):
            return submissions

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
        response_list = []
        for submission in submissions:
            response = post_create_viewer_launch_url(
                submission.turnitin_submission_id, payload
            )
            response_list.append(response.json())

        return Response(response_list)

    @staticmethod
    def get_submissions(ora_submission_id: str) -> QuerySet | Response:
        """
        Retrieve the Turnitin submissions for the user.

        Args:
            ora_submission_id (str): The unique identifier for the submission in
                the Open Response Assessment (ORA) system.

        Returns:
            list: The list of Turnitin submissions for the user.
        """
        submissions = TurnitinSubmission.objects.filter(
            ora_submission_id=ora_submission_id
        )
        if not submissions:
            return api_error(
                f"ORA Submission with id='{ora_submission_id}' not found.",
                status.HTTP_404_NOT_FOUND,
            )
        return submissions
