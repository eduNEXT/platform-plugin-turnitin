"""This module contains tests for the filters module."""

from unittest import TestCase
from unittest.mock import Mock

from platform_plugin_turnitin.extensions.filters import ORASubmissionViewTurnitinWarning


class TestORASubmissionViewTurnitinWarning(TestCase):
    """Tests for the ORASubmissionViewTurnitinWarning class."""

    def setUp(self) -> None:
        self.pipeline_step = ORASubmissionViewTurnitinWarning(
            filter_type=Mock(), running_pipeline=Mock()
        )
        self.context = {"key": "value"}
        self.template_name = "template_name"
        self.new_template_name = "turnitin/oa_response.html"

    def test_run_filter(self):
        """
        Test that the `run_filter` method returns a dictionary with the context and the new template name.

        Expected result: The dictionary contains the context and the new template name.
        """
        result = self.pipeline_step.run_filter(self.context, self.template_name)

        self.assertEqual(result["context"], self.context)
        self.assertEqual(result["template_name"], self.new_template_name)
