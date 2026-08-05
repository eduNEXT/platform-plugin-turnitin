""" Tests for the TurnitinClient class."""

from unittest import TestCase
from unittest.mock import Mock, call, patch

from django.utils import translation
from rest_framework import status
from rest_framework.response import Response

from platform_plugin_turnitin.api.v1.views import TurnitinClient

VIEWS_MODULE_PATH = "platform_plugin_turnitin.api.v1.views"
SUBMISSION_RETRY_ATTEMPTS = 3


class TestTurnitinClient(TestCase):
    """Test the TurnitinClient class."""

    def setUp(self):
        self.user = Mock()
        self.user.id = 1
        self.user.email = "john@doe.com"
        self.user.profile.name = "John Doe"
        self.user.username = "john_doe"
        self.file = Mock()
        self.file.name = "file.txt"
        self.turnitin_client = TurnitinClient(self.user, self.file)
        self.ora_submission_id = "test-ora-submission-id"
        self.turnitin_submission_id = "test-turnitin-submission-id"

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_accept_eula_version")
    def test_accept_eula_agreement(
        self, mock_post_accept: Mock, mock_get_current_datetime: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `accept_eula_agreement` method.

        Expected result:
            - `post_accept_eula_version` function is called with the correct payload and version
            - `accept_eula_agreement` method returns the correct response.
        """
        current_datetime = "2023-11-21T15:30:00Z"
        mock_get_current_datetime.return_value = current_datetime
        mock_resolve_version.return_value = "v1beta"
        expected_payload = {
            "user_id": str(self.user.id),
            "accepted_timestamp": current_datetime,
            "language": "en-US",
        }
        expected_response = Mock(status_code=status.HTTP_200_OK)
        mock_post_accept.return_value = expected_response

        result = self.turnitin_client.accept_eula_agreement()

        mock_post_accept.assert_called_once_with(expected_payload, version="v1beta")
        self.assertEqual(result, expected_response)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_accept_eula_version")
    def test_accept_eula_agreement_spanish_locale(
        self, mock_post_accept: Mock, mock_get_current_datetime: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `accept_eula_agreement` method sends "es-ES" when Spanish is the active language.

        Expected result:
            - `post_accept_eula_version` function is called with `"language": "es-ES"`.
        """
        mock_get_current_datetime.return_value = "2023-11-21T15:30:00Z"
        mock_resolve_version.return_value = "v1beta"

        with translation.override("es"):
            self.turnitin_client.accept_eula_agreement()

        self.assertEqual(mock_post_accept.call_args.args[0]["language"], "es-ES")

    @patch(f"{VIEWS_MODULE_PATH}.put_upload_submission_file_content")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission")
    @patch(f"{VIEWS_MODULE_PATH}.Response")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.create_turnitin_submission_object")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.has_accepted_eula")
    def test_upload_turnitin_submission_file_success(
        self,
        mock_has_accepted_eula: Mock,
        mock_create_turnitin_submission: Mock,
        mock_response: Mock,
        mock_model: Mock,
        mock_put_upload_file: Mock,
    ):
        """
        Test the `upload_turnitin_submission_file` method.

        Expected result:
            - `create_turnitin_submission_object` function is called
            - `TurnitinSubmission` model is created with the correct parameters
            - `put_upload_submission_file_content` function is called with the correct parameters
            - `upload_turnitin_submission_file` method returns the correct response.
        """
        mock_has_accepted_eula.return_value = True
        mock_create_turnitin_submission.return_value = Mock(
            status_code=status.HTTP_201_CREATED,
            json=Mock(return_value={"id": self.turnitin_submission_id}),
        )

        result = self.turnitin_client.upload_turnitin_submission_file(
            self.ora_submission_id
        )

        mock_create_turnitin_submission.assert_called_once()
        mock_model.assert_called_once_with(
            user=self.user,
            ora_submission_id=self.ora_submission_id,
            turnitin_submission_id=self.turnitin_submission_id,
            file_name=self.file.name,
        )
        mock_put_upload_file.assert_called_once_with(
            self.turnitin_submission_id, self.file
        )
        mock_response.assert_called_once_with(mock_put_upload_file.return_value.json())
        self.assertEqual(result, mock_response.return_value)

    @patch(f"{VIEWS_MODULE_PATH}.put_upload_submission_file_content")
    @patch(f"{VIEWS_MODULE_PATH}.Response")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.create_turnitin_submission_object")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.has_accepted_eula")
    def test_upload_turnitin_submission_file_error(
        self,
        mock_has_accepted_eula: Mock,
        mock_create_turnitin_submission: Mock,
        mock_response: Mock,
        mock_put_upload_file: Mock,
    ):
        """
        Test the `upload_turnitin_submission_file` method with error response.

        Expected result:
            - `create_turnitin_submission_object` function is called
            - `put_upload_submission_file_content` function is not called
            - `upload_turnitin_submission_file` method returns the correct response.
        """
        mock_has_accepted_eula.return_value = True
        mock_create_turnitin_submission.return_value = Mock(
            status_code=status.HTTP_400_BAD_REQUEST,
            json=Mock(return_value={"error": "Bad request"}),
        )

        result = self.turnitin_client.upload_turnitin_submission_file(
            self.ora_submission_id
        )

        mock_create_turnitin_submission.assert_called_once()
        mock_put_upload_file.assert_not_called()
        mock_response.assert_called_once_with(
            mock_create_turnitin_submission.return_value.json()
        )
        self.assertEqual(result, mock_response.return_value)

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.create_turnitin_submission_object")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.has_accepted_eula")
    def test_upload_turnitin_submission_file_eula_not_accepted(
        self, mock_has_accepted_eula: Mock, mock_create_turnitin_submission: Mock
    ):
        """
        Test the `upload_turnitin_submission_file` method when the EULA has not been accepted.

        Expected result:
            - `create_turnitin_submission_object` is not called.
            - The response has a 451 status code.
        """
        mock_has_accepted_eula.return_value = False

        result = self.turnitin_client.upload_turnitin_submission_file(
            self.ora_submission_id
        )

        mock_create_turnitin_submission.assert_not_called()
        self.assertEqual(result.status_code, status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.get_eula_acceptance_by_user")
    def test_has_accepted_eula_true(self, mock_get_eula_acceptance: Mock, mock_resolve_version: Mock):
        """
        Test the `has_accepted_eula` method when Turnitin confirms acceptance.

        Expected result: The method returns True.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_acceptance.return_value = Mock(ok=True)

        result = self.turnitin_client.has_accepted_eula()

        self.assertTrue(result)
        mock_get_eula_acceptance.assert_called_once_with(str(self.user.id), version="v1beta")

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.sleep")
    @patch(f"{VIEWS_MODULE_PATH}.get_eula_acceptance_by_user")
    def test_has_accepted_eula_persistent_failure(
        self, mock_get_eula_acceptance: Mock, mock_sleep: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `has_accepted_eula` method when Turnitin never confirms acceptance.

        Expected result:
            - The method returns False after retrying `SUBMISSION_RETRY_ATTEMPTS` times.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_acceptance.return_value = Mock(ok=False)

        result = self.turnitin_client.has_accepted_eula()

        self.assertFalse(result)
        self.assertEqual(mock_get_eula_acceptance.call_count, SUBMISSION_RETRY_ATTEMPTS)
        self.assertEqual(mock_sleep.call_count, SUBMISSION_RETRY_ATTEMPTS - 1)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.sleep")
    @patch(f"{VIEWS_MODULE_PATH}.get_eula_acceptance_by_user")
    def test_has_accepted_eula_recovers_after_retry(
        self, mock_get_eula_acceptance: Mock, mock_sleep: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `has_accepted_eula` method recovers after a transient check failure.

        Expected result: The method returns True once the check succeeds on retry.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_acceptance.side_effect = [Mock(ok=False), Mock(ok=True)]

        result = self.turnitin_client.has_accepted_eula()

        self.assertTrue(result)
        self.assertEqual(mock_get_eula_acceptance.call_count, 2)
        mock_sleep.assert_called_once()

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_create_submission")
    def test_create_turnitin_submission_object(
        self, mock_post_create: Mock, mock_get_current_datetime: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `create_turnitin_submission_object` method.

        Expected result:
            - `post_create_submission` function is called with the correct payload
        """
        current_datetime = "2023-11-21T16:00:00Z"
        mock_get_current_datetime.return_value = current_datetime
        mock_resolve_version.return_value = "v1beta"
        expected_response = Mock(status_code=status.HTTP_201_CREATED)
        mock_post_create.return_value = expected_response
        expected_payload = {
            "owner": str(self.user.id),
            "title": f"{self.file.name}-{self.user.username}",
            "submitter": str(self.user.id),
            "owner_default_permission_set": "LEARNER",
            "submitter_default_permission_set": "LEARNER",
            "extract_text_only": False,
            "eula": {
                "accepted_timestamp": current_datetime,
                "language": "en-US",
                "version": "v1beta",
            },
            "metadata": {
                "group": None,
                "group_context": None,
                "owners": [
                    {
                        "id": str(self.user.id),
                        "given_name": self.turnitin_client.first_name,
                        "family_name": self.turnitin_client.last_name,
                        "email": self.user.email,
                    }
                ],
                "submitter": {
                    "id": str(self.user.id),
                    "given_name": self.turnitin_client.first_name,
                    "family_name": self.turnitin_client.last_name,
                    "email": self.user.email,
                },
                "original_submitted_time": current_datetime,
            },
        }

        result = self.turnitin_client.create_turnitin_submission_object()

        mock_post_create.assert_called_once_with(expected_payload)
        self.assertEqual(result, expected_response)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_create_submission")
    def test_create_turnitin_submission_object_with_group(
        self, mock_post_create: Mock, mock_get_current_datetime: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `create_turnitin_submission_object` method sends `group`/`group_context` when provided.

        Expected result:
            - `post_create_submission` is called with the `group` and `group_context` values
                the `TurnitinClient` was constructed with.
        """
        mock_get_current_datetime.return_value = "2023-11-21T16:00:00Z"
        mock_resolve_version.return_value = "v1beta"
        mock_post_create.return_value = Mock(status_code=status.HTTP_201_CREATED)
        block_id = "block-v1:edX+DemoX+Demo_Course+type@openassessment+block@abc123"
        course_id = "course-v1:edX+DemoX+Demo_Course"
        turnitin_client = TurnitinClient(self.user, self.file, group=block_id, group_context=course_id)

        turnitin_client.create_turnitin_submission_object()

        metadata = mock_post_create.call_args.args[0]["metadata"]
        self.assertEqual(metadata["group"], block_id)
        self.assertEqual(metadata["group_context"], course_id)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.sleep")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_create_submission")
    def test_create_turnitin_submission_object_persistent_failure(
        self, mock_post_create: Mock, mock_get_current_datetime: Mock, mock_sleep: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `create_turnitin_submission_object` method with a persistent failure.

        Expected result:
            - `post_create_submission` is retried `SUBMISSION_RETRY_ATTEMPTS` times.
            - The last (failing) response is returned.
        """
        mock_get_current_datetime.return_value = "2023-11-21T16:00:00Z"
        mock_resolve_version.return_value = "v1beta"
        failed_response = Mock(status_code=status.HTTP_400_BAD_REQUEST)
        mock_post_create.return_value = failed_response

        result = self.turnitin_client.create_turnitin_submission_object()

        self.assertEqual(mock_post_create.call_count, SUBMISSION_RETRY_ATTEMPTS)
        self.assertEqual(mock_sleep.call_count, SUBMISSION_RETRY_ATTEMPTS - 1)
        self.assertEqual(result, failed_response)

    @patch(f"{VIEWS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{VIEWS_MODULE_PATH}.sleep")
    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_create_submission")
    def test_create_turnitin_submission_object_recovers_after_retry(
        self, mock_post_create: Mock, mock_get_current_datetime: Mock, mock_sleep: Mock, mock_resolve_version: Mock
    ):
        """
        Test the `create_turnitin_submission_object` method recovers after a transient failure.

        Expected result:
            - `post_create_submission` is called again after a failed attempt.
            - The successful response is returned.
        """
        mock_get_current_datetime.return_value = "2023-11-21T16:00:00Z"
        mock_resolve_version.return_value = "v1beta"
        failed_response = Mock(status_code=status.HTTP_400_BAD_REQUEST)
        success_response = Mock(status_code=status.HTTP_201_CREATED)
        mock_post_create.side_effect = [failed_response, success_response]

        result = self.turnitin_client.create_turnitin_submission_object()

        self.assertEqual(mock_post_create.call_count, 2)
        mock_sleep.assert_called_once()
        self.assertEqual(result, success_response)

    @patch(f"{VIEWS_MODULE_PATH}.get_submission_info")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_submission_status_success(
        self, mock_get_submissions: Mock, mock_get_submission_info: Mock
    ):
        """
        Test the `get_submission_status` method.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `get_submission_info` function is called the correct number of
                times with the correct parameters
        """
        turnitin_submission_1 = Mock(turnitin_submission_id="id1")
        turnitin_submission_2 = Mock(turnitin_submission_id="id2")
        mock_get_submissions.return_value = [
            turnitin_submission_1,
            turnitin_submission_2,
        ]
        mock_response_1 = Mock(json=Mock(return_value={"status": "COMPLETED"}))
        mock_response_2 = Mock(json=Mock(return_value={"status": "PROCESSING"}))
        mock_get_submission_info.side_effect = [mock_response_1, mock_response_2]

        result = self.turnitin_client.get_submission_status(self.ora_submission_id)

        mock_get_submissions.assert_called_once_with(self.ora_submission_id)
        mock_get_submission_info.assert_has_calls([call("id1"), call("id2")])
        self.assertEqual(
            result.data, [{"status": "COMPLETED"}, {"status": "PROCESSING"}]
        )

    @patch(f"{VIEWS_MODULE_PATH}.get_submission_info")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_submission_status_error_response(
        self, mock_get_submissions: Mock, mock_get_submission_info: Mock
    ):
        """
        Test the `get_submission_status` method with error response.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `get_submission_info` function is not called
        """
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        response = self.turnitin_client.get_submission_status(self.ora_submission_id)

        self.assertEqual(response, error_response)
        mock_get_submission_info.assert_not_called()

    @patch(f"{VIEWS_MODULE_PATH}.put_generate_similarity_report")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_generate_similarity_report_success(
        self, mock_get_submissions: Mock, mock_put_generate: Mock
    ):
        """
        Test the `generate_similarity_report` method.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `put_generate_similarity_report` function is called the correct number of
                times with the correct parameters
        """
        turnitin_submission_1 = Mock(turnitin_submission_id="id1")
        turnitin_submission_2 = Mock(turnitin_submission_id="id2")
        mock_get_submissions.return_value = [
            turnitin_submission_1,
            turnitin_submission_2,
        ]
        mock_response_1 = Mock(json=Mock(return_value={"message": "SUCCESSFUL"}))
        mock_response_2 = Mock(json=Mock(return_value={"message": "SUCCESSFUL"}))
        mock_put_generate.side_effect = [mock_response_1, mock_response_2]

        result = self.turnitin_client.generate_similarity_report(self.ora_submission_id)

        mock_get_submissions.assert_called_once_with(self.ora_submission_id)
        mock_put_generate.assert_has_calls(
            [
                call("id1", {"test_key": "test_value"}),
                call("id2", {"test_key": "test_value"}),
            ]
        )
        self.assertEqual(
            result.data, [{"message": "SUCCESSFUL"}, {"message": "SUCCESSFUL"}]
        )

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_generate_similarity_report_error_response(
        self, mock_get_submissions: Mock
    ):
        """
        Test the `generate_similarity_report` method with error response.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `generate_similarity_report` method returns the correct response.
        """
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        result = self.turnitin_client.generate_similarity_report(self.ora_submission_id)

        self.assertEqual(result, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.get_similarity_report_info")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_similarity_report_status_success(
        self, mock_get_submissions: Mock, mock_get_report_info: Mock
    ):
        """
        Test the `get_similarity_report_status` method.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `get_similarity_report_info` function is called the correct number of
                times with the correct parameters
        """
        turnitin_submission_1 = Mock(turnitin_submission_id="id1")
        turnitin_submission_2 = Mock(turnitin_submission_id="id2")
        mock_get_submissions.return_value = [
            turnitin_submission_1,
            turnitin_submission_2,
        ]
        mock_response_1 = Mock(json=Mock(return_value={"status": "COMPLETED"}))
        mock_response_2 = Mock(json=Mock(return_value={"status": "PROCESSING"}))
        mock_get_report_info.side_effect = [mock_response_1, mock_response_2]

        result = self.turnitin_client.get_similarity_report_status(
            self.ora_submission_id
        )

        mock_get_submissions.assert_called_once_with(self.ora_submission_id)
        mock_get_report_info.assert_has_calls([call("id1"), call("id2")])
        self.assertEqual(
            result.data, [{"status": "COMPLETED"}, {"status": "PROCESSING"}]
        )

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_similarity_report_status_error_response(
        self, mock_get_submissions: Mock
    ):
        """
        Test the `get_similarity_report_status` method with error response.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `get_similarity_report_status` method returns error response.
        """
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        result = self.turnitin_client.get_similarity_report_status(
            self.ora_submission_id
        )

        self.assertEqual(result, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.post_create_viewer_launch_url")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_create_similarity_viewer_success(
        self, mock_get_submissions: Mock, mock_post_create: Mock
    ):
        """
        Test the `create_similarity_viewer` method.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `post_create_viewer_launch_url` function is called the correct number of
                times with the correct parameters
        """
        turnitin_submission_1 = Mock(turnitin_submission_id="id1", file_name="file1")
        turnitin_submission_2 = Mock(turnitin_submission_id="id2", file_name="file2")
        mock_get_submissions.return_value = [
            turnitin_submission_1,
            turnitin_submission_2,
        ]
        mock_response_1 = Mock(json=Mock(return_value={"viewer_url": "url1"}))
        mock_response_2 = Mock(json=Mock(return_value={"viewer_url": "url2"}))
        mock_post_create.side_effect = [mock_response_1, mock_response_2]

        result = self.turnitin_client.create_similarity_viewer(self.ora_submission_id)

        mock_get_submissions.assert_called_once_with(self.ora_submission_id)
        expected_payload = {
            "viewer_user_id": str(self.user.id),
            "locale": "en-US",
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
                "family_name": self.turnitin_client.last_name,
                "given_name": self.turnitin_client.first_name,
            },
            "sidebar": {"default_mode": "similarity"},
        }
        mock_post_create.assert_has_calls(
            [call("id1", expected_payload), call("id2", expected_payload)]
        )
        self.assertEqual(
            result.data,
            [
                {"url": "url1", "file_name": "file1"},
                {"url": "url2", "file_name": "file2"},
            ],
        )

    @patch(f"{VIEWS_MODULE_PATH}.post_create_viewer_launch_url")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_create_similarity_viewer_spanish_locale(
        self, mock_get_submissions: Mock, mock_post_create: Mock
    ):
        """
        Test the `create_similarity_viewer` method sends "es-ES" when Spanish is the active language.

        Expected result:
            - `post_create_viewer_launch_url` function is called with `"locale": "es-ES"`.
        """
        mock_get_submissions.return_value = [Mock(turnitin_submission_id="id1", file_name="file1")]
        mock_post_create.return_value = Mock(json=Mock(return_value={"viewer_url": "url1"}))

        with translation.override("es"):
            self.turnitin_client.create_similarity_viewer(self.ora_submission_id)

        self.assertEqual(mock_post_create.call_args.args[1]["locale"], "es-ES")

    @patch(f"{VIEWS_MODULE_PATH}.post_create_viewer_launch_url")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_create_similarity_viewer_skip_not_success(
        self, mock_get_submissions: Mock, mock_post_create: Mock
    ):
        """
        Test the `create_similarity_viewer` method with submissions that are not in
        success status.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `post_create_viewer_launch_url` function is called the correct number of
                times with the correct parameters
            - `create_similarity_viewer` method returns the correct response.
        """
        turnitin_submission_1 = Mock(turnitin_submission_id="id1", file_name="file1")
        turnitin_submission_2 = Mock(turnitin_submission_id="id2", file_name="file2")
        turnitin_submission_3 = Mock(turnitin_submission_id="id3", file_name="file3")
        mock_get_submissions.return_value = [
            turnitin_submission_1,
            turnitin_submission_2,
            turnitin_submission_3,
        ]
        mock_response_1 = Mock(json=Mock(return_value={"success": False}))
        mock_response_2 = Mock(json=Mock(return_value={"success": False}))
        mock_response_3 = Mock(json=Mock(return_value={"viewer_url": "url3"}))
        mock_post_create.side_effect = [
            mock_response_1,
            mock_response_2,
            mock_response_3,
        ]

        result = self.turnitin_client.create_similarity_viewer(self.ora_submission_id)

        mock_get_submissions.assert_called_once_with(self.ora_submission_id)
        expected_payload = {
            "viewer_user_id": str(self.user.id),
            "locale": "en-US",
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
                "family_name": self.turnitin_client.last_name,
                "given_name": self.turnitin_client.first_name,
            },
            "sidebar": {"default_mode": "similarity"},
        }
        mock_post_create.assert_has_calls(
            [
                call("id1", expected_payload),
                call("id2", expected_payload),
                call("id3", expected_payload),
            ]
        )
        self.assertEqual(result.data, [{"url": "url3", "file_name": "file3"}])

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_create_similarity_viewer_error_response(self, mock_get_submissions: Mock):
        """
        Test the `create_similarity_viewer` method with error response.

        Expected result:
            - `get_submissions` function is called with the correct parameters
            - `create_similarity_viewer` method returns an error response.
        """
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        result = self.turnitin_client.create_similarity_viewer(self.ora_submission_id)

        self.assertEqual(result, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission.objects")
    def test_get_submissions_success(self, mock_objects: Mock):
        """
        Test the `get_submissions` method.

        Expected result:
            - `get_submissions` method returns the correct response.
        """
        mock_submission = Mock()
        mock_objects.filter.return_value = [mock_submission]

        result = self.turnitin_client.get_submissions(self.ora_submission_id)

        mock_objects.filter.assert_called_once_with(
            ora_submission_id=self.ora_submission_id
        )
        self.assertEqual(result, [mock_submission])

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission.objects")
    def test_get_submissions_not_found(self, mock_objects: Mock):
        """
        Test the `get_submissions` method when no submission is found.

        Expected result:
            - `get_submissions` method returns an error response.
        """
        mock_objects.filter.return_value = []

        result = self.turnitin_client.get_submissions(self.ora_submission_id)

        mock_objects.filter.assert_called_once_with(
            ora_submission_id=self.ora_submission_id
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            result.data["error"],
            f"ORA Submission with id='{self.ora_submission_id}' not found.",
        )
