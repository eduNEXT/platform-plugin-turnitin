"""Filters for the Turnitin plugin."""

from openedx_filters import PipelineStep


class CheckTurnitinForPlagiarism(PipelineStep):
    """Check if Turnitin plagiarism check is enabled."""

    def run_filter(  # pylint: disable=unused-argument, disable=arguments-differ
        self, context: dict, template_name: str
    ) -> dict:
        """
        Execute filter that loads the template with a warning message that notifies the user
        that the Turnitin plagiarism check is enabled.

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
