"""Tests for the handlers module."""

from unittest.mock import Mock, patch

from django.test import TestCase
from django.test.utils import override_settings

from platform_plugin_turnitin.handlers import ora_submission_created


class TestHandlers(TestCase):
    """Tests for the handlers module."""

    def setUp(self) -> None:
        self.submission = Mock(
            uuid="submission_uuid",
            location="block_id",
            anonymous_user_id="user_id",
            answer=Mock(parts=[], file_names=[], file_urls=[]),
        )

    @patch("platform_plugin_turnitin.handlers.ora_submission_created_task.delay")
    @patch("platform_plugin_turnitin.handlers.enabled_in_course")
    def test_ora_submission_created_all_disabled(self, mock_enabled_in_course: Mock, mock_call_task: Mock):
        """Test `ora_submission_created` when Turnitin submission is disabled globally and for the course."""
        mock_enabled_in_course.return_value = False

        ora_submission_created(self.submission)

        mock_call_task.assert_not_called()

    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    @patch("platform_plugin_turnitin.handlers.ora_submission_created_task.delay")
    def test_ora_submission_created_global_enabled(self, mock_call_task: Mock):
        """Test `ora_submission_created` when Turnitin submission is enabled globally."""
        ora_submission_created(self.submission)

        mock_call_task.assert_called_once_with(
            self.submission.uuid,
            self.submission.anonymous_user_id,
            self.submission.answer.parts,
            self.submission.answer.file_names,
            self.submission.answer.file_urls,
        )

    @patch("platform_plugin_turnitin.handlers.ora_submission_created_task.delay")
    @patch("platform_plugin_turnitin.handlers.enabled_in_course")
    def test_ora_submission_created_course_enabled(self, mock_enabled_in_course: Mock, mock_call_task: Mock):
        """Test `ora_submission_created` when Turnitin submission is enabled for the course."""
        mock_enabled_in_course.return_value = True

        ora_submission_created(self.submission)

        mock_call_task.assert_called_once_with(
            self.submission.uuid,
            self.submission.anonymous_user_id,
            self.submission.answer.parts,
            self.submission.answer.file_names,
            self.submission.answer.file_urls,
        )
