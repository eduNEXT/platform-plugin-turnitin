"""Filters for the Turnitin plugin."""

from openedx_filters import PipelineStep


class ORASubmissionViewTurnitinWarning(PipelineStep):
    """Add warning message about Turnitin to the ORA submission view."""

    def run_filter(  # pylint: disable=unused-argument, disable=arguments-differ
        self, context: dict, template_name: str
    ) -> dict:
        """
        Execute filter that loads the submission template with a warning message that
        notifies the user that the submission will be sent to Turnitin.

        Args:
            context (dict): The context dictionary.
            template_name (str): ORA template name.

        Returns:
            dict: The context dictionary and the template name.
        """
        return {
            "context": context,
            "template_name": "turnitin/oa_response.html",
        }
