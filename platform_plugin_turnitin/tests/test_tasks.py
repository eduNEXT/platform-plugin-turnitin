"""Tests for the tasks module."""

from unittest import TestCase
from unittest.mock import Mock, call, patch

from rest_framework import status

from platform_plugin_turnitin.tasks import (
    generate_similarity_report,
    get_submission_status,
    is_submission_complete,
    ora_submission_created_task,
    send_file_to_turnitin,
    send_text_to_turnitin,
    send_uploaded_files_to_turnitin,
    upload_turnitin_submission,
)

TASKS_MODULE_PATH = "platform_plugin_turnitin.tasks"


MAX_REQUEST_RETRIES = 3
SECONDS_TO_WAIT_BETWEEN_RETRIES = 1


class TestOraSubmissionCreatedTask(TestCase):
    """Tests for the ora_submission_created_task function."""

    def setUp(self) -> None:
        self.submission_id = "test-submission-id"
        self.file_downloads = [{"file": "file1"}, {"file": "file2"}]
        self.user = Mock()
        self.user.id = "1"
        self.file = Mock()

    @patch(f"{TASKS_MODULE_PATH}.submissions_api.get_submission_and_student")
    @patch(f"{TASKS_MODULE_PATH}.user_by_anonymous_id")
    @patch(f"{TASKS_MODULE_PATH}.send_text_to_turnitin")
    @patch(f"{TASKS_MODULE_PATH}.send_uploaded_files_to_turnitin")
    @patch(f"{TASKS_MODULE_PATH}.is_submission_complete")
    @patch(f"{TASKS_MODULE_PATH}.generate_similarity_report")
    def test_ora_submission_created_task(
        self,
        mock_generate_similarity_report: Mock,
        mock_is_submission_complete: Mock,
        mock_send_uploaded_files_to_turnitin: Mock,
        mock_send_text_to_turnitin: Mock,
        mock_user_by_anonymous_id: Mock,
        mock_get_submission_and_student: Mock,
    ):
        mock_get_submission_and_student.return_value = {
            "student_item": {"student_id": self.user.id},
            "answer": "answer",
        }
        mock_user_by_anonymous_id.return_value = self.user
        mock_is_submission_complete.return_value = True

        ora_submission_created_task(self.submission_id, self.file_downloads)

        mock_get_submission_and_student.assert_called_once_with(self.submission_id)
        mock_user_by_anonymous_id.assert_called_once_with(self.user.id)
        mock_send_text_to_turnitin.assert_called_once_with(
            self.submission_id, self.user, "answer"
        )
        mock_send_uploaded_files_to_turnitin.assert_called_once_with(
            self.submission_id,
            self.user,
            self.file_downloads,
        )
        mock_is_submission_complete.assert_called()
        mock_generate_similarity_report.assert_called_once_with(
            self.submission_id, self.user
        )

    @patch(f"{TASKS_MODULE_PATH}.submissions_api.get_submission_and_student")
    @patch(f"{TASKS_MODULE_PATH}.user_by_anonymous_id")
    @patch(f"{TASKS_MODULE_PATH}.send_text_to_turnitin")
    @patch(f"{TASKS_MODULE_PATH}.send_uploaded_files_to_turnitin")
    @patch(f"{TASKS_MODULE_PATH}.is_submission_complete")
    @patch(f"{TASKS_MODULE_PATH}.generate_similarity_report")
    @patch(f"{TASKS_MODULE_PATH}.sleep")
    def test_ora_submission_created_task_with_retries(
        self,
        mock_sleep: Mock,
        mock_generate_similarity_report: Mock,
        mock_is_submission_complete: Mock,
        mock_send_uploaded_files_to_turnitin: Mock,
        mock_send_text_to_turnitin: Mock,
        mock_user_by_anonymous_id: Mock,
        mock_get_submission_and_student: Mock,
    ):
        mock_get_submission_and_student.return_value = {
            "student_item": {"student_id": self.user.id},
            "answer": "answer",
        }
        mock_user_by_anonymous_id.return_value = self.user
        mock_is_submission_complete.side_effect = [False] * (
            MAX_REQUEST_RETRIES - 1
        ) + [True]

        ora_submission_created_task(self.submission_id, self.file_downloads)

        mock_get_submission_and_student.assert_called_once_with(self.submission_id)
        mock_user_by_anonymous_id.assert_called_once_with(self.user.id)
        mock_send_text_to_turnitin.assert_called_once_with(
            self.submission_id, self.user, "answer"
        )
        mock_send_uploaded_files_to_turnitin.assert_called_once_with(
            self.submission_id, self.user, self.file_downloads
        )
        self.assertEqual(mock_is_submission_complete.call_count, MAX_REQUEST_RETRIES)
        mock_generate_similarity_report.assert_called_once_with(
            self.submission_id, self.user
        )
        self.assertEqual(mock_sleep.call_count, MAX_REQUEST_RETRIES - 1)

    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_text_to_turnitin(self, mock_send_file_to_turnitin: Mock):
        answer = {"parts": [{"text": "part1"}, {"text": "part2"}]}

        send_text_to_turnitin(self.submission_id, self.user, answer)

        calls = [
            call(
                self.submission_id, self.user, "part1".encode("utf-8"), "response.txt"
            ),
            call(
                self.submission_id, self.user, "part2".encode("utf-8"), "response.txt"
            ),
        ]
        mock_send_file_to_turnitin.assert_has_calls(calls)

    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_text_to_turnitin_empty_answer(self, mock_send_file_to_turnitin: Mock):
        """Tests the function with an empty answer."""
        answer = {"parts": []}

        send_text_to_turnitin(self.submission_id, self.user, answer)

        self.assertFalse(mock_send_file_to_turnitin.called)

    @patch(f"{TASKS_MODULE_PATH}.requests.get")
    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_uploaded_files_to_turnitin(
        self, mock_send_file_to_turnitin: Mock, mock_get: Mock
    ):
        file_downloads = [
            {"name": "file1.txt", "download_url": "/download/file1.txt"},
            {"name": "file2.doc", "download_url": "/download/file2.doc"},
            {"name": "file3.jpg", "download_url": "/download/file3.jpg"},
        ]
        mock_get.return_value = Mock(ok=True, content=b"file content")

        send_uploaded_files_to_turnitin(self.submission_id, self.user, file_downloads)

        calls = [
            call(self.submission_id, self.user, b"file content", "file1.txt"),
            call(self.submission_id, self.user, b"file content", "file2.doc"),
        ]
        mock_send_file_to_turnitin.assert_has_calls(calls)
        self.assertEqual(mock_send_file_to_turnitin.call_count, 2)

    @patch(f"{TASKS_MODULE_PATH}.requests.get")
    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_uploaded_files_to_turnitin_failure_to_download(
        self, mock_send_file_to_turnitin: Mock, mock_get: Mock
    ):
        file_link = "/download/file1.txt"
        file_downloads = [{"name": "file1.txt", "download_url": file_link}]
        exception_message = f"Failed to download file from {file_link}"
        mock_get.return_value = Mock(ok=False)

        with self.assertRaises(Exception) as context:
            send_uploaded_files_to_turnitin(
                self.submission_id, self.user, file_downloads
            )

        mock_send_file_to_turnitin.assert_not_called()
        self.assertEqual(exception_message, str(context.exception))

    @patch(f"{TASKS_MODULE_PATH}.tempfile.NamedTemporaryFile")
    @patch(f"{TASKS_MODULE_PATH}.upload_turnitin_submission")
    def test_send_file_to_turnitin(
        self, mock_upload_turnitin_submission: Mock, mock_temp_file: Mock
    ):
        file_content = b"file content"
        filename = "file.txt"
        mock_file = mock_temp_file.return_value.__enter__.return_value
        mock_file.name = filename

        send_file_to_turnitin(self.submission_id, self.user, file_content, filename)

        mock_temp_file.assert_called_once()
        mock_file.write.assert_called_once_with(file_content)
        mock_file.seek.assert_called_once_with(0)
        mock_upload_turnitin_submission.assert_called_once_with(
            self.submission_id, self.user, mock_file
        )

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_upload_turnitin_submission(self, mock_turnitin_client: Mock):
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.accept_eula_agreement.return_value.ok = True

        upload_turnitin_submission(self.submission_id, self.user, self.file)

        mock_turnitin_client.assert_called_once_with(self.user, self.file)
        mock_turnitin_client_instance.accept_eula_agreement.assert_called_once()
        mock_turnitin_client_instance.upload_turnitin_submission_file.assert_called_once_with(
            self.submission_id
        )

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_upload_turnitin_submission_eula_failure(self, mock_turnitin_client: Mock):
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.accept_eula_agreement.return_value.ok = False

        with self.assertRaises(Exception) as context:
            upload_turnitin_submission(self.submission_id, self.user, self.file)

        self.assertEqual("Failed to accept the EULA agreement.", str(context.exception))
        mock_turnitin_client.assert_called_once_with(self.user, self.file)
        mock_turnitin_client_instance.accept_eula_agreement.assert_called_once()
        mock_turnitin_client_instance.upload_turnitin_submission_file.assert_not_called()

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_non_ok_status_code(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_400_BAD_REQUEST
        )

        result = is_submission_complete(self.submission_id, self.user)

        self.assertFalse(result)
        mock_get_submission_status.assert_called_once_with(
            self.submission_id, self.user
        )
        mock_log_info.assert_not_called()

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_all_complete_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "COMPLETE"}, {"status": "COMPLETE"}],
        )

        result = is_submission_complete(self.submission_id, self.user)

        self.assertTrue(result)
        mock_get_submission_status.assert_called_once_with(
            self.submission_id, self.user
        )
        mock_log_info.assert_called_once_with(
            f"Submission [{self.submission_id}] is complete."
        )

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_all_error_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "ERROR"}, {"status": "ERROR"}],
        )

        result = is_submission_complete(self.submission_id, self.user)

        self.assertTrue(result)
        mock_get_submission_status.assert_called_once_with(
            self.submission_id, self.user
        )
        mock_log_info.assert_called_once_with(
            f"Submission [{self.submission_id}] is complete."
        )

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_processing_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "COMPLETE"}, {"status": "PROCESSING"}],
        )

        result = is_submission_complete(self.submission_id, self.user)

        self.assertFalse(result)
        mock_get_submission_status.assert_called_once_with(
            self.submission_id, self.user
        )
        mock_log_info.assert_called_once_with(
            f"Submission [{self.submission_id}] is not complete. Checking again..."
        )

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_get_submission_status(self, mock_turnitin_client: Mock):
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK
        )

        result = get_submission_status(self.submission_id, self.user)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.get_submission_status.assert_called_once_with(
            self.submission_id
        )

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_get_submission_status_with_error(self, mock_turnitin_client: Mock):
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.get_submission_status.return_value = Mock(
            status_code=status.HTTP_400_BAD_REQUEST
        )

        result = get_submission_status(self.submission_id, self.user)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.get_submission_status.assert_called_once_with(
            self.submission_id
        )

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_generate_similarity_report(self, mock_turnitin_client: Mock):
        mock_turnitin_client_instance = mock_turnitin_client.return_value

        generate_similarity_report(self.submission_id, self.user)

        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.generate_similarity_report.assert_called_once_with(
            self.submission_id
        )
