""" Tests for the api views."""

from unittest.mock import Mock, patch

from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from platform_plugin_turnitin.api.v1.views import (
    TurnitinSimilarityReportAPIView,
    TurnitinSubmissionAPIView,
    TurnitinUploadFileAPIView,
    TurnitinViewerAPIView,
)

VIEWS_MODULE_PATH = "platform_plugin_turnitin.api.v1.views"
UTILS_MODULE_PATH = "platform_plugin_turnitin.api.utils"

get_course_overview_patch = patch(f"{UTILS_MODULE_PATH}.get_course_overview_or_none")
course_staff_role_patch = patch(f"{UTILS_MODULE_PATH}.CourseStaffRole")
course_instructor_role_patch = patch(f"{UTILS_MODULE_PATH}.CourseInstructorRole")
accept_eula_patch = patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.accept_eula_agreement")
upload_turnitin_submission_patch = patch(
    f"{VIEWS_MODULE_PATH}.TurnitinClient.upload_turnitin_submission_file"
)
get_submission_patch = patch(
    f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submission_status"
)
generate_similarity_report_patch = patch(
    f"{VIEWS_MODULE_PATH}.TurnitinClient.generate_similarity_report"
)
get_similarity_report_patch = patch(
    f"{VIEWS_MODULE_PATH}.TurnitinClient.get_similarity_report_status"
)
create_similarity_viewer_patch = patch(
    f"{VIEWS_MODULE_PATH}.TurnitinClient.create_similarity_viewer"
)


class TurnitinAPITestMixin(APITestCase):
    """Base test case for the Turnitin API."""

    def setUp(self):
        self.factory = APIRequestFactory()

        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.ora_submission_id = "917ed4b1-f684-4dfa-90e5-a31fdd6177af"

        self.user = Mock()
        self.user.email = "john@doe.com"
        self.user.profile.name = "John Doe"
        self.user.is_staff = True
        self.course = Mock()

    def response(self, view, method: str, path_name: str):
        """..."""
        url = reverse(
            path_name,
            kwargs={"ora_submission_id": self.ora_submission_id},
        )
        request = self.factory.generic(method, url)
        force_authenticate(request, user=self.user)
        return view(
            request,
            course_id=self.course_id,
            ora_submission_id=self.ora_submission_id,
        )

    def course_key_not_valid(self, response: HttpResponse):
        """..."""
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["field_errors"]["course_id"],
            f"The supplied course_id='{self.course_id}' key is not valid.",
        )

    def course_not_found(self, response: HttpResponse):
        """..."""
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["field_errors"]["course_id"],
            f"The course with course_id='{self.course_id}' is not found.",
        )

    def user_does_not_have_access(self, response: HttpResponse):
        """..."""
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["error"],
            "The user does not have access to consume the endpoint.",
        )


class TurnitinUploadFileAPIViewTest(TurnitinAPITestMixin):
    """Tests for the TurnitinViewerAPIView."""

    def setUp(self):
        super().setUp()
        self.view = TurnitinUploadFileAPIView.as_view()

    def post_response(self) -> HttpResponse:
        """..."""
        return self.response(self.view, "POST", "turnitin-api:v1:upload-file")

    @upload_turnitin_submission_patch
    @accept_eula_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_upload_file(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        accept_eula_mock: Mock,
        upload_turnitin_submission_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        accept_eula_mock.return_value = Mock(ok=True)
        upload_turnitin_submission_mock.return_value = Response(
            status=status.HTTP_200_OK
        )

        response = self.post_response()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @accept_eula_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_upload_file_accept_eula_error(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        accept_eula_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        accept_eula_mock.return_value = Mock(
            ok=False,
            json=Mock(return_value="EULA not accepted"),
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        result = self.post_response()

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["error"], "EULA not accepted")

    def test_upload_file_course_key_not_valid(self):
        """..."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        response = self.post_response()

        self.course_key_not_valid(response)

    @get_course_overview_patch
    def test_upload_file_course_not_found(self, get_course_overview_mock: Mock):
        """..."""
        get_course_overview_mock.return_value = None

        result = self.post_response()

        self.course_not_found(result)


class TurnitinSubmissionAPIViewTest(TurnitinAPITestMixin):
    """Tests for the TurnitinSubmissionAPIView."""

    def setUp(self):
        super().setUp()
        self.view = TurnitinSubmissionAPIView.as_view()

    def get_response(self) -> HttpResponse:
        """..."""
        return self.response(self.view, "GET", "turnitin-api:v1:get-submission")

    @get_submission_patch
    @accept_eula_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_submission(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        accept_eula_mock: Mock,
        get_submission_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        accept_eula_mock.return_value = Mock(ok=True)
        get_submission_mock.return_value = Response(status=status.HTTP_200_OK)

        response = self.get_response()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_submission_course_key_not_valid(self):
        """..."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        response = self.get_response()

        self.course_key_not_valid(response)

    @get_course_overview_patch
    def test_get_submission_course_not_found(self, get_course_overview_mock: Mock):
        """..."""
        get_course_overview_mock.return_value = None

        response = self.get_response()

        self.course_not_found(response)

    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_submission_user_does_not_have_access(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        self.user.is_staff = False
        course_staff_role_mock.return_value.has_user.return_value = False
        course_instructor_role_mock.return_value.has_user.return_value = False

        response = self.get_response()

        self.user_does_not_have_access(response)


class TurnitinSimilarityReportAPIViewTest(TurnitinAPITestMixin):
    """Tests for the TurnitinSimilarityReportAPIView."""

    def setUp(self):
        super().setUp()
        self.view = TurnitinSimilarityReportAPIView.as_view()

    def get_response(self) -> HttpResponse:
        """..."""
        return self.response(self.view, "GET", "turnitin-api:v1:get-similarity-report")

    def put_response(self) -> HttpResponse:
        """..."""
        return self.response(
            self.view, "PUT", "turnitin-api:v1:generate-similarity-report"
        )

    @get_similarity_report_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_similarity_report(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_similarity_report_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        get_similarity_report_mock.return_value = Response(status=status.HTTP_200_OK)

        result = self.get_response()

        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_get_similarity_report_course_key_not_valid(self):
        """..."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        result = self.get_response()

        self.course_key_not_valid(result)

    @get_course_overview_patch
    def test_get_similarity_report_course_not_found(
        self, get_course_overview_mock: Mock
    ):
        """..."""
        get_course_overview_mock.return_value = None

        result = self.get_response()

        self.course_not_found(result)

    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_similarity_report_user_does_not_have_access(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        self.user.is_staff = False
        course_staff_role_mock.return_value.has_user.return_value = False
        course_instructor_role_mock.return_value.has_user.return_value = False

        result = self.get_response()

        self.user_does_not_have_access(result)

    @generate_similarity_report_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_generate_similarity_report(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        generate_similarity_report_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        generate_similarity_report_mock.return_value = Response(
            status=status.HTTP_200_OK
        )

        result = self.put_response()

        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_generate_similarity_report_course_key_not_valid(self):
        """..."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        response = self.put_response()

        self.course_key_not_valid(response)

    @get_course_overview_patch
    def test_generate_similarity_report_course_not_found(
        self, get_course_overview_mock: Mock
    ):
        """..."""
        get_course_overview_mock.return_value = None

        result = self.put_response()

        self.course_not_found(result)

    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_generate_similarity_report_user_does_not_have_access(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        self.user.is_staff = False
        course_staff_role_mock.return_value.has_user.return_value = False
        course_instructor_role_mock.return_value.has_user.return_value = False

        result = self.put_response()

        self.user_does_not_have_access(result)


class TurnitinViewerAPIViewTest(TurnitinAPITestMixin):
    """Tests for the TurnitinViewerAPIView."""

    def setUp(self):
        super().setUp()
        self.view = TurnitinViewerAPIView.as_view()

    def get_response(self) -> HttpResponse:
        """..."""
        return self.response(self.view, "GET", "turnitin-api:v1:viewer-url")

    @create_similarity_viewer_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_viewer_url(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        create_similarity_viewer_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        course_staff_role_mock.return_value.has_user.return_value = True
        course_instructor_role_mock.return_value.has_user.return_value = True
        create_similarity_viewer_mock.return_value = Response(status=status.HTTP_200_OK)

        result = self.get_response()

        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_get_viewer_url_course_key_not_valid(self):
        """..."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        result = self.get_response()

        self.course_key_not_valid(result)

    @get_course_overview_patch
    def test_get_viewer_url_course_not_found(self, get_course_overview_mock: Mock):
        """..."""
        get_course_overview_mock.return_value = None

        result = self.get_response()

        self.course_not_found(result)

    @course_instructor_role_patch
    @course_staff_role_patch
    @get_course_overview_patch
    def test_get_viewer_url_user_does_not_have_access(
        self,
        get_course_overview_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
    ):
        """..."""
        get_course_overview_mock.return_value = self.course
        self.user.is_staff = False
        course_staff_role_mock.return_value.has_user.return_value = False
        course_instructor_role_mock.return_value.has_user.return_value = False

        result = self.get_response()

        self.user_does_not_have_access(result)
