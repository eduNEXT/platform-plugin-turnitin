"""Filters for the Turnitin plugin."""

from django.conf import settings
from opaque_keys.edx.keys import UsageKey
from openedx_filters import PipelineStep

from platform_plugin_turnitin.utils import enabled_in_course


class ORASubmissionViewTurnitinWarning(PipelineStep):
    """Add warning message about Turnitin to the ORA submission view."""

    def run_filter(self, context: dict, template_name: str) -> dict:  # pylint: disable=arguments-differ
        """
        Execute filter that loads the submission template with a warning message that
        notifies the user that the submission will be sent to Turnitin, and a checkbox that
        calls the accept-eula endpoint before allowing submission.

        If the Turnitin feature is not enabled globally or in the course, the original
        template is returned.

        Args:
            context (dict): The context dictionary.
            template_name (str): ORA template name.

        Returns:
            dict: The context dictionary and the template name.
        """
        if settings.ENABLE_TURNITIN_SUBMISSION or enabled_in_course(context["xblock_id"]):
            course_id = str(UsageKey.from_string(context["xblock_id"]).course_key)
            context = {
                **context,
                "turnitin_accept_eula_url": f"/platform-plugin-turnitin/{course_id}/api/v1/accept-eula/",
            }
            return {
                "context": context,
                "template_name": "turnitin/oa_response.html",
            }

        return {
            "context": context,
            "template_name": template_name,
        }
