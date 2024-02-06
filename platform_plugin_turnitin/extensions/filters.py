"""Filters for the Turnitin plugin."""

from openedx_filters import PipelineStep


class CheckTurnitinForPlagiarism(PipelineStep):
    """Check if Turnitin plagiarism check is enabled."""

    def run_filter(
        self, context: dict, template_name: str
    ):  # pylint: disable=unused-argument, arguments-differ
        """
        Execute filter that loads the template with a warning message that notifies the user
        that the Turnitin plagiarism check is enabled.

        Args:
            context (dict): ORA context.
            template_name (str): ORA template name.

        Returns:
            dict: The context with the new template name.
        """
        return {
            "context": context,
            "template_name": "turnitin/ora.html",
        }
