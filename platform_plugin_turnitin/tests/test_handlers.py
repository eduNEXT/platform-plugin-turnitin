"""Tests for the handlers module."""

from unittest.mock import Mock, patch

from django.test import TestCase
from django.test.utils import override_settings

from platform_plugin_turnitin.handlers import ora_submission_created


class TestHandlers(TestCase):
    """Tests for the handlers module."""

    def setUp(self) -> None:
        self.submission = Mock(location="test_block_id")

    @patch("platform_plugin_turnitin.handlers.call_ora_submission_created_task")
    @patch("platform_plugin_turnitin.handlers.modulestore")
    @patch("platform_plugin_turnitin.handlers.UsageKey")
    def test_ora_submission_created_all_disabled(
        self, mock_usage_key: Mock, mock_modulestore: Mock, mock_call_task: Mock
    ):
        """Test `ora_submission_created` when Turnitin submission is disabled globally and for the course."""
        mock_usage_key.from_string.return_value.course_key = "course_key"
        mock_modulestore.return_value.get_course.return_value = Mock(
            other_course_settings={"ENABLE_TURNITIN_SUBMISSION": False},
        )

        ora_submission_created(self.submission)

        mock_call_task.assert_not_called()

    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    @patch("platform_plugin_turnitin.handlers.call_ora_submission_created_task")
    def test_ora_submission_created_global_enabled(self, mock_call_task: Mock):
        """Test `ora_submission_created` when Turnitin submission is enabled globally."""
        ora_submission_created(self.submission)

        mock_call_task.assert_called_once_with(self.submission)

    @patch("platform_plugin_turnitin.handlers.call_ora_submission_created_task")
    @patch("platform_plugin_turnitin.handlers.modulestore")
    @patch("platform_plugin_turnitin.handlers.UsageKey")
    def test_ora_submission_created_course_enabled(
        self, mock_usage_key: Mock, mock_modulestore: Mock, mock_call_task: Mock
    ):
        """Test `ora_submission_created` when Turnitin submission is enabled for the course."""
        mock_usage_key.from_string.return_value.course_key = "course_key"
        mock_modulestore.return_value.get_course.return_value = Mock(
            other_course_settings={"ENABLE_TURNITIN_SUBMISSION": True},
        )

        ora_submission_created(self.submission)

        mock_call_task.assert_called_once_with(self.submission)
