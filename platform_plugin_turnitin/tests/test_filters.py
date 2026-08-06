"""This module contains tests for the filters module."""

from unittest import TestCase
from unittest.mock import Mock, patch

from django.test.utils import override_settings
from requests.exceptions import RequestException

from platform_plugin_turnitin.extensions.filters import ORASubmissionViewTurnitinWarning

FILTERS_MODULE_PATH = "platform_plugin_turnitin.extensions.filters"


class TestORASubmissionViewTurnitinWarning(TestCase):
    """Tests for the ORASubmissionViewTurnitinWarning class."""

    def setUp(self) -> None:
        self.pipeline_step = ORASubmissionViewTurnitinWarning(filter_type=Mock(), running_pipeline=Mock())
        self.xblock_id = "block-v1:edX+DemoX+Demo_Course+type@openassessment+block@abc123"
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.context = {"key": "value", "xblock_id": self.xblock_id}
        self.template_name = "template_name"
        self.new_template_name = "turnitin/oa_response.html"

    @patch("platform_plugin_turnitin.extensions.filters.enabled_in_course")
    def test_run_filter_turnitin_submission_disabled(self, mock_enabled_in_course: Mock):
        """
        Test `run_filter` method when Turnitin submission is disabled.

        Expected result: The dictionary contains the same context and template name.
        """
        mock_enabled_in_course.return_value = False

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"], self.context)
        self.assertEqual(result["template_name"], self.template_name)

    @patch(f"{FILTERS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{FILTERS_MODULE_PATH}.get_eula_page")
    @patch(f"{FILTERS_MODULE_PATH}.enabled_in_course")
    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    def test_run_filter_turnitin_submission_enabled_by_global_setting(
        self, mock_enabled_in_course: Mock, mock_get_eula_page: Mock, mock_resolve_version: Mock
    ):
        """
        Test `run_filter` method when Turnitin submission is enabled by the global setting.

        Expected result: The dictionary contains the context, EULA content, and the new
            template name.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_page.return_value = Mock(ok=True, text="<p>EULA content</p>")

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"]["key"], "value")
        self.assertEqual(
            result["context"]["turnitin_accept_eula_url"],
            f"/platform-plugin-turnitin/{self.course_id}/api/v1/accept-eula/",
        )
        self.assertEqual(result["context"]["turnitin_eula_content"], "<p>EULA content</p>")
        self.assertEqual(result["template_name"], self.new_template_name)
        mock_enabled_in_course.assert_not_called()
        mock_get_eula_page.assert_called_once_with(version="v1beta")

    @patch(f"{FILTERS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{FILTERS_MODULE_PATH}.get_eula_page")
    @patch(f"{FILTERS_MODULE_PATH}.enabled_in_course")
    def test_run_filter_turnitin_submission_enabled_by_course_setting(
        self, mock_enabled_in_course: Mock, mock_get_eula_page: Mock, mock_resolve_version: Mock
    ):
        """
        Test `run_filter` method when Turnitin submission is enabled by the course setting.

        Expected result: The dictionary contains the context, EULA content, and the new
            template name.
        """
        mock_enabled_in_course.return_value = True
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_page.return_value = Mock(ok=True, text="<p>EULA content</p>")

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"]["key"], "value")
        self.assertEqual(
            result["context"]["turnitin_accept_eula_url"],
            f"/platform-plugin-turnitin/{self.course_id}/api/v1/accept-eula/",
        )
        self.assertEqual(result["context"]["turnitin_eula_content"], "<p>EULA content</p>")
        self.assertEqual(result["template_name"], self.new_template_name)

    @patch(f"{FILTERS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{FILTERS_MODULE_PATH}.get_eula_page")
    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    def test_run_filter_eula_content_non_ok_response(self, mock_get_eula_page: Mock, mock_resolve_version: Mock):
        """
        Test `run_filter` falls back to no inline content when Turnitin returns a non-OK response.

        Expected result: `turnitin_eula_content` is None; the template still renders.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_page.return_value = Mock(ok=False, status_code=500)

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertIsNone(result["context"]["turnitin_eula_content"])
        self.assertEqual(result["template_name"], self.new_template_name)

    @patch(f"{FILTERS_MODULE_PATH}.resolve_current_eula_version")
    @patch(f"{FILTERS_MODULE_PATH}.get_eula_page")
    @override_settings(ENABLE_TURNITIN_SUBMISSION=True)
    def test_run_filter_eula_content_request_exception(self, mock_get_eula_page: Mock, mock_resolve_version: Mock):
        """
        Test `run_filter` falls back to no inline content when fetching the EULA raises.

        Expected result: `turnitin_eula_content` is None; the template still renders.
        """
        mock_resolve_version.return_value = "v1beta"
        mock_get_eula_page.side_effect = RequestException

        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertIsNone(result["context"]["turnitin_eula_content"])
        self.assertEqual(result["template_name"], self.new_template_name)
