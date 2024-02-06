"""Filters for the Turnitin plugin."""

from openedx_filters import PipelineStep


class CheckTurnitinForPlagiarism(PipelineStep):
    """Check if Turnitin plagiarism check is enabled."""

    def run_filter(
        self, template_name: str
    ):  # pylint: disable=unused-argument, arguments-differ
        """
        Execute filter that loads the template with a warning message that notifies the user
        that the Turnitin plagiarism check is enabled.

        Args:
            template_name (str): ORA template name.

        Returns:
            dict: The new template name.
        """
        return {
            "template_name": "turnitin/oa_response.html",
        }
