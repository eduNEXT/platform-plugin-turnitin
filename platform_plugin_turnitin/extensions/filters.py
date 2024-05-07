"""Filters for the Turnitin plugin."""

from crum import get_current_request
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from openedx_filters import PipelineStep

from platform_plugin_turnitin.edxapp_wrapper.modulestore import modulestore


class ORASubmissionViewTurnitinWarning(PipelineStep):
    """Add warning message about Turnitin to the ORA submission view."""

    def run_filter(self, context: dict, template_name: str) -> dict:  # pylint: disable=arguments-differ
        """
        Execute filter that loads the submission template with a warning message that
        notifies the user that the submission will be sent to Turnitin.

        Args:
            context (dict): The context dictionary.
            template_name (str): ORA template name.

        Returns:
            dict: The context dictionary and the template name.
        """
        if settings.ENABLE_TURNITIN_SUBMISSION:
            return {
                "context": context,
                "template_name": "turnitin/oa_response.html",
            }

        course_id = get_current_request().resolver_match.kwargs.get("course_id")
        course_key = CourseKey.from_string(course_id)
        course_block = modulestore().get_course(course_key)
        enable_in_course = course_block.other_course_settings.get("ENABLE_TURNITIN_SUBMISSION", False)

        if enable_in_course:
            return {
                "context": context,
                "template_name": "turnitin/oa_response.html",
            }

        return {
            "context": context,
            "template_name": template_name,
        }
