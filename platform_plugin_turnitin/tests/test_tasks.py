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
        self.submission_uuid = "test-submission-uuid"
        self.anonymous_user_id = "test-anonymous-user-id"
        self.parts = [{"text": "part1"}, {"text": "part2"}]
        self.file_names = ["file1.txt", "file2.doc"]
        self.file_urls = ["/download/file1.txt", "/download/file2.doc"]
        self.user = Mock()
        self.file = Mock()

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
    ):
        """
        Test the `ora_submission_created_task` function.

        Expected result:
            - `user_by_anonymous_id` is called once with the anonymous_user_id.
            - `send_text_to_turnitin` is called once with the submission_id, user and parts.
            - `send_uploaded_files_to_turnitin` is called once with the submission_uuid,
                user, file_names and file_urls.
        """
        mock_user_by_anonymous_id.return_value = self.user
        mock_is_submission_complete.return_value = True

        ora_submission_created_task(
            self.submission_uuid, self.anonymous_user_id, self.parts, self.file_names, self.file_urls
        )

        mock_user_by_anonymous_id.assert_called_once_with(self.anonymous_user_id)
        mock_send_text_to_turnitin.assert_called_once_with(self.submission_uuid, self.user, self.parts)
        mock_send_uploaded_files_to_turnitin.assert_called_once_with(
            self.submission_uuid,
            self.user,
            self.file_names,
            self.file_urls,
        )
        mock_is_submission_complete.assert_called()
        mock_generate_similarity_report.assert_called_once_with(self.submission_uuid, self.user)

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
    ):
        """
        Test the `ora_submission_created_task` function with retries.

        Expected result:
            - `user_by_anonymous_id` is called once with the anonymous_user_id.
            - `send_text_to_turnitin` is called once with the submission_uuid, user and parts.
            - `send_uploaded_files_to_turnitin` is called once with the submission_uuid,
                user, file_names and file_urls.
            - `is_submission_complete` is called MAX_REQUEST_RETRIES times.
            - `generate_similarity_report` is called once.
        """
        mock_user_by_anonymous_id.return_value = self.user
        mock_is_submission_complete.side_effect = [False] * (MAX_REQUEST_RETRIES - 1) + [True]

        ora_submission_created_task(
            self.submission_uuid, self.anonymous_user_id, self.parts, self.file_names, self.file_urls
        )

        mock_user_by_anonymous_id.assert_called_once_with(self.anonymous_user_id)
        mock_send_text_to_turnitin.assert_called_once_with(self.submission_uuid, self.user, self.parts)
        mock_send_uploaded_files_to_turnitin.assert_called_once_with(
            self.submission_uuid, self.user, self.file_names, self.file_urls
        )
        self.assertEqual(mock_is_submission_complete.call_count, MAX_REQUEST_RETRIES)
        mock_generate_similarity_report.assert_called_once_with(self.submission_uuid, self.user)
        self.assertEqual(mock_sleep.call_count, MAX_REQUEST_RETRIES - 1)

    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_text_to_turnitin(self, mock_send_file_to_turnitin: Mock):
        """
        Test the `send_text_to_turnitin` function.

        Expected result:
            - `send_file_to_turnitin` is called twice with the submission_id,
                user and text parts.
        """
        response_txt = "Student's Text Response Part {}.txt"

        send_text_to_turnitin(self.submission_uuid, self.user, self.parts)

        calls = [
            call(self.submission_uuid, self.user, "part1".encode("utf-8"), response_txt.format(1)),
            call(self.submission_uuid, self.user, "part2".encode("utf-8"), response_txt.format(2)),
        ]
        mock_send_file_to_turnitin.assert_has_calls(calls)

    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_text_to_turnitin_empty_answer(self, mock_send_file_to_turnitin: Mock):
        """
        Test the `send_text_to_turnitin` function with an empty answer.

        Expected result:
            - `send_file_to_turnitin` function is not called.
        """
        send_text_to_turnitin(self.submission_uuid, self.user, [])

        self.assertFalse(mock_send_file_to_turnitin.called)

    @patch(f"{TASKS_MODULE_PATH}.requests.get")
    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_uploaded_files_to_turnitin(self, mock_send_file_to_turnitin: Mock, mock_get: Mock):
        """
        Test the `send_uploaded_files_to_turnitin` function.

        Expected result:
            - `send_file_to_turnitin` is called twice with the submission_uuid,
                user, file_names and file_urls.
        """
        file_names = ["file1.txt", "file2.doc"]
        file_urls = ["/download/file1.txt", "/download/file2.doc"]
        mock_get.return_value = Mock(ok=True, content=b"file content")

        send_uploaded_files_to_turnitin(self.submission_uuid, self.user, file_names, file_urls)

        calls = [
            call(self.submission_uuid, self.user, b"file content", "file1.txt"),
            call(self.submission_uuid, self.user, b"file content", "file2.doc"),
        ]
        mock_send_file_to_turnitin.assert_has_calls(calls)
        self.assertEqual(mock_send_file_to_turnitin.call_count, 2)

    @patch(f"{TASKS_MODULE_PATH}.requests.get")
    @patch(f"{TASKS_MODULE_PATH}.send_file_to_turnitin")
    def test_send_uploaded_files_to_turnitin_failure_to_download(
        self, mock_send_file_to_turnitin: Mock, mock_get: Mock
    ):
        """
        Test the `send_uploaded_files_to_turnitin` function with a failure to download a file.

        Expected result:
            - An exception is raised with the correct message.
            - `send_file_to_turnitin` function is not called.
        """
        file_link = "/download/file1.txt"
        file_names = ["file1.txt"]
        file_urls = [file_link]
        exception_message = f"Failed to download file from {file_link}"
        mock_get.return_value = Mock(ok=False)

        with self.assertRaises(Exception) as context:
            send_uploaded_files_to_turnitin(self.submission_uuid, self.user, file_names, file_urls)

        mock_send_file_to_turnitin.assert_not_called()
        self.assertEqual(exception_message, str(context.exception))

    @patch(f"{TASKS_MODULE_PATH}.tempfile.NamedTemporaryFile")
    @patch(f"{TASKS_MODULE_PATH}.upload_turnitin_submission")
    def test_send_file_to_turnitin(self, mock_upload_turnitin_submission: Mock, mock_temp_file: Mock):
        """
        Test the `send_file_to_turnitin` function.

        Expected result:
            - `tempfile.NamedTemporaryFile` is called once.
            - `upload_turnitin_submission` is called once with the submission_id,
                user and file content.
        """
        file_content = b"file content"
        filename = "file.txt"
        mock_file = mock_temp_file.return_value.__enter__.return_value
        mock_file.name = filename

        send_file_to_turnitin(self.submission_uuid, self.user, file_content, filename)

        mock_temp_file.assert_called_once()
        mock_file.write.assert_called_once_with(file_content)
        mock_file.seek.assert_called_once_with(0)
        mock_upload_turnitin_submission.assert_called_once_with(self.submission_uuid, self.user, mock_file)

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_upload_turnitin_submission(self, mock_turnitin_client: Mock):
        """
        Test the `upload_turnitin_submission` function.

        Expected result:
            - `TurnitinClient` is called once with the user and file.
            - `accept_eula_agreement` is called once.
            - `upload_turnitin_submission_file` is called once with the submission_id.
        """
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.accept_eula_agreement.return_value.ok = True

        upload_turnitin_submission(self.submission_uuid, self.user, self.file)

        mock_turnitin_client.assert_called_once_with(self.user, self.file)
        mock_turnitin_client_instance.accept_eula_agreement.assert_called_once()
        mock_turnitin_client_instance.upload_turnitin_submission_file.assert_called_once_with(self.submission_uuid)

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_upload_turnitin_submission_eula_failure(self, mock_turnitin_client: Mock):
        """
        Test the `upload_turnitin_submission` function with a failure to accept the EULA agreement.

        Expected result:
            - An exception is raised with the correct message.
            - `TurnitinClient` is called once with the user and file.
            - `accept_eula_agreement` is called once.
            - `upload_turnitin_submission_file` is not called.
        """
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.accept_eula_agreement.return_value.ok = False

        with self.assertRaises(Exception) as context:
            upload_turnitin_submission(self.submission_uuid, self.user, self.file)

        self.assertEqual("Failed to accept the EULA agreement.", str(context.exception))
        mock_turnitin_client.assert_called_once_with(self.user, self.file)
        mock_turnitin_client_instance.accept_eula_agreement.assert_called_once()
        mock_turnitin_client_instance.upload_turnitin_submission_file.assert_not_called()

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_non_ok_status_code(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        """
        Test the `is_submission_complete` function with a non-OK status code.

        Expected result:
            - The function returns False.
            - `get_submission_status` is called once with the submission_id and user.
            - `log.info` is not called.
        """
        mock_get_submission_status.return_value = Mock(status_code=status.HTTP_400_BAD_REQUEST)

        result = is_submission_complete(self.submission_uuid, self.user)

        self.assertFalse(result)
        mock_get_submission_status.assert_called_once_with(self.submission_uuid, self.user)
        mock_log_info.assert_not_called()

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_all_complete_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        """
        Test the `is_submission_complete` function with all submissions complete.

        Expected result:
            - The function returns True.
            - `get_submission_status` is called once with the submission_id and user.
            - `log.info` is called once with the correct message.
        """
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "COMPLETE"}, {"status": "COMPLETE"}],
        )

        result = is_submission_complete(self.submission_uuid, self.user)

        self.assertTrue(result)
        mock_get_submission_status.assert_called_once_with(self.submission_uuid, self.user)
        mock_log_info.assert_called_once_with(f"Submission [{self.submission_uuid}] is complete.")

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_all_error_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        """
        Test the `is_submission_complete` function with all submissions in error.

        Expected result:
            - The function returns True.
            - `get_submission_status` is called once with the submission_id and user.
            - `log.info` is called once with the correct message.
        """
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "ERROR"}, {"status": "ERROR"}],
        )

        result = is_submission_complete(self.submission_uuid, self.user)

        self.assertTrue(result)
        mock_get_submission_status.assert_called_once_with(self.submission_uuid, self.user)
        mock_log_info.assert_called_once_with(f"Submission [{self.submission_uuid}] is complete.")

    @patch(f"{TASKS_MODULE_PATH}.get_submission_status")
    @patch(f"{TASKS_MODULE_PATH}.log.info")
    def test_is_submission_complete_with_processing_submissions(
        self, mock_log_info: Mock, mock_get_submission_status: Mock
    ):
        """
        Test the `is_submission_complete` function with processing submissions.

        Expected result:
            - The function returns False.
            - `get_submission_status` is called once with the submission_id and user.
            - `log.info` is called once with the correct message.
        """
        mock_get_submission_status.return_value = Mock(
            status_code=status.HTTP_200_OK,
            data=[{"status": "COMPLETE"}, {"status": "PROCESSING"}],
        )

        result = is_submission_complete(self.submission_uuid, self.user)

        self.assertFalse(result)
        mock_get_submission_status.assert_called_once_with(self.submission_uuid, self.user)
        mock_log_info.assert_called_once_with(f"Submission [{self.submission_uuid}] is not complete. Checking again...")

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_get_submission_status(self, mock_turnitin_client: Mock):
        """
        Test the `get_submission_status` function.

        Expected result:
            - `TurnitinClient` is called once with the user.
            - `get_submission_status` is called once with the submission_id.
        """
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.get_submission_status.return_value = Mock(status_code=status.HTTP_200_OK)

        result = get_submission_status(self.submission_uuid, self.user)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.get_submission_status.assert_called_once_with(self.submission_uuid)

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_get_submission_status_with_error(self, mock_turnitin_client: Mock):
        """
        Test the `get_submission_status` function with an error.

        Expected result:
            - The function returns a response with the correct status code.
            - `TurnitinClient` is called once with the user.
            - `get_submission_status` is called once with the submission_id.
        """
        mock_turnitin_client_instance = mock_turnitin_client.return_value
        mock_turnitin_client_instance.get_submission_status.return_value = Mock(status_code=status.HTTP_400_BAD_REQUEST)

        result = get_submission_status(self.submission_uuid, self.user)

        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.get_submission_status.assert_called_once_with(self.submission_uuid)

    @patch(f"{TASKS_MODULE_PATH}.TurnitinClient")
    def test_generate_similarity_report(self, mock_turnitin_client: Mock):
        """
        Test the `generate_similarity_report` function.

        Expected result:
            - `TurnitinClient` is called once with the user.
            - `generate_similarity_report` is called once with the submission_id.
        """
        mock_turnitin_client_instance = mock_turnitin_client.return_value

        generate_similarity_report(self.submission_uuid, self.user)

        mock_turnitin_client.assert_called_once_with(self.user)
        mock_turnitin_client_instance.generate_similarity_report.assert_called_once_with(self.submission_uuid)
