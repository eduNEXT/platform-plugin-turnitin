"""This module contains tests for the filters module."""

from unittest import TestCase
from unittest.mock import Mock, patch

from django.test.utils import override_settings
from opaque_keys.edx.keys import UsageKey

from platform_plugin_turnitin.extensions.filters import ORASubmissionViewTurnitinWarning


class TestORASubmissionViewTurnitinWarning(TestCase):
    """Tests for the ORASubmissionViewTurnitinWarning class."""

    def setUp(self) -> None:
        self.pipeline_step = ORASubmissionViewTurnitinWarning(filter_type=Mock(), running_pipeline=Mock())
        self.context = {"key": "value", "xblock_id": "test_xblock_id"}
        self.template_name = "template_name"
        self.new_template_name = "turnitin/oa_response.html"

    @patch("platform_plugin_turnitin.extensions.filters.modulestore")
    @patch.object(UsageKey, "from_string")
    def test_run_filter_turnitin_submission_disabled(self, mock_from_string: Mock, mock_modulestore: Mock):
        """
        Test `run_filter` method when Turnitin submission is disabled.

        Expected result: The dictionary contains the same context and template name.
        """
        mock_from_string.return_value.course_key = "test_course_key"
        mock_modulestore.return_value.get_course.return_value = Mock(
            other_course_settings={"ENABLE_TURNITIN_SUBMISSION": False},
        )

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"], self.context)
        self.assertEqual(result["template_name"], self.template_name)

    @patch("platform_plugin_turnitin.extensions.filters.modulestore")
    @patch.object(UsageKey, "from_string")
    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    def test_run_filter_turnitin_submission_enabled_by_global_setting(
        self, mock_from_string: Mock, mock_modulestore: Mock
    ):
        """
        Test `run_filter` method when Turnitin submission is enabled by the global setting.

        Expected result: The dictionary contains the context and the new template name.
        """
        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"], self.context)
        self.assertEqual(result["template_name"], self.new_template_name)
        mock_from_string.assert_not_called()
        mock_modulestore.assert_not_called()

    @patch("platform_plugin_turnitin.extensions.filters.modulestore")
    @patch.object(UsageKey, "from_string")
    def test_run_filter_turnitin_submission_enabled_by_course_setting(
        self, mock_from_string: Mock, mock_modulestore: Mock
    ):
        """
        Test `run_filter` method when Turnitin submission is enabled by the course setting.

        Expected result: The dictionary contains the context and the new template name.
        """
        mock_from_string.return_value.course_key = "test_course_key"
        mock_modulestore.return_value.get_course.return_value = Mock(
            other_course_settings={"ENABLE_TURNITIN_SUBMISSION": True},
        )

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"], self.context)
        self.assertEqual(result["template_name"], self.new_template_name)
