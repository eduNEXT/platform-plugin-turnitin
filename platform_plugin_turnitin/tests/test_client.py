""" Tests for the TurnitinClient class."""

from unittest import TestCase
from unittest.mock import Mock, call, patch

from rest_framework import status
from rest_framework.response import Response

from platform_plugin_turnitin.api.v1.views import TurnitinClient

VIEWS_MODULE_PATH = "platform_plugin_turnitin.api.v1.views"


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

    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_accept_eula_version")
    def test_accept_eula_agreement(
        self, mock_post_accept: Mock, mock_get_current_datetime: Mock
    ):
        current_datetime = "2023-11-21T15:30:00Z"
        mock_get_current_datetime.return_value = current_datetime
        expected_payload = {
            "user_id": str(self.user.id),
            "accepted_timestamp": current_datetime,
            "language": "en-US",
        }
        expected_response = Mock(status_code=status.HTTP_200_OK)
        mock_post_accept.return_value = expected_response

        result = self.turnitin_client.accept_eula_agreement()

        mock_post_accept.assert_called_once_with(expected_payload)
        self.assertEqual(result, expected_response)

    @patch(f"{VIEWS_MODULE_PATH}.put_upload_submission_file_content")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission")
    @patch(f"{VIEWS_MODULE_PATH}.Response")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.create_turnitin_submission_object")
    def test_upload_turnitin_submission_file_success(
        self,
        mock_create_turnitin_submission: Mock,
        mock_response: Mock,
        mock_model: Mock,
        mock_put_upload_file: Mock,
    ):
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
    def test_upload_turnitin_submission_file_error(
        self,
        mock_create_turnitin_submission: Mock,
        mock_response: Mock,
        mock_put_upload_file: Mock,
    ):
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

    @patch(f"{VIEWS_MODULE_PATH}.get_current_datetime")
    @patch(f"{VIEWS_MODULE_PATH}.post_create_submission")
    def test_create_turnitin_submission_object(
        self, mock_post_create: Mock, mock_get_current_datetime: Mock
    ):
        current_datetime = "2023-11-21T16:00:00Z"
        mock_get_current_datetime.return_value = current_datetime
        expected_response = Mock(status_code=status.HTTP_201_CREATED)
        mock_post_create.return_value = expected_response
        expected_payload = {
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
                        "given_name": self.turnitin_client.first_name,
                        "family_name": self.turnitin_client.last_name,
                        "email": self.user.email,
                    }
                ],
                "submitter": {
                    "id": self.user.id,
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

    @patch(f"{VIEWS_MODULE_PATH}.get_submission_info")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_submission_status_success(
        self, mock_get_submissions: Mock, mock_get_submission_info: Mock
    ):
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

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_submission_status_error_response(self, mock_get_submissions: Mock):
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        response = self.turnitin_client.get_submission_status(self.ora_submission_id)

        self.assertEqual(response, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.put_generate_similarity_report")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_generate_similarity_report_success(
        self, mock_get_submissions: Mock, mock_put_generate: Mock
    ):
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
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        result = self.turnitin_client.generate_similarity_report(self.ora_submission_id)

        self.assertEqual(result, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.get_similarity_report_info")
    @patch(f"{VIEWS_MODULE_PATH}.TurnitinClient.get_submissions")
    def test_get_similarity_report_status_success(
        self, mock_get_submissions: Mock, mock_get_report_info: Mock
    ):
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
    def test_create_similarity_viewer_skip_not_success(
        self, mock_get_submissions: Mock, mock_post_create: Mock
    ):
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
        error_response = Response(status=status.HTTP_400_BAD_REQUEST)
        mock_get_submissions.return_value = error_response

        result = self.turnitin_client.create_similarity_viewer(self.ora_submission_id)

        self.assertEqual(result, error_response)

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission.objects")
    def test_get_submissions_success(self, mock_objects: Mock):
        mock_submission = Mock()
        mock_objects.filter.return_value = [mock_submission]

        result = self.turnitin_client.get_submissions(self.ora_submission_id)

        mock_objects.filter.assert_called_once_with(
            ora_submission_id=self.ora_submission_id
        )
        self.assertEqual(result, [mock_submission])

    @patch(f"{VIEWS_MODULE_PATH}.TurnitinSubmission.objects")
    def test_get_submissions_not_found(self, mock_objects: Mock):
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
