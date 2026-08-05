"""Filters for the Turnitin plugin."""

from logging import getLogger

from django.conf import settings
from opaque_keys.edx.keys import UsageKey
from openedx_filters import PipelineStep
from requests.exceptions import RequestException

from platform_plugin_turnitin.turnitin_client.handlers import get_eula_page
from platform_plugin_turnitin.utils import enabled_in_course, resolve_current_eula_version

log = getLogger(__name__)


class ORASubmissionViewTurnitinWarning(PipelineStep):
    """Add warning message about Turnitin to the ORA submission view."""

    def run_filter(self, context: dict, template_name: str) -> dict:  # pylint: disable=arguments-differ
        """
        Execute filter that loads the submission template with a notice that the submission
        will be sent to Turnitin, Turnitin's current EULA text rendered inline, and a checkbox
        that calls the accept-eula endpoint before allowing submission.

        If the Turnitin feature is not enabled globally or in the course, the original
        template is returned. If fetching the EULA content fails, the template falls back to
        linking out to it rather than failing the whole page render.

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
                "turnitin_eula_content": self._get_eula_content(),
            }
            return {
                "context": context,
                "template_name": "turnitin/oa_response.html",
            }

        return {
            "context": context,
            "template_name": template_name,
        }

    def _get_eula_content(self):
        """
        Fetch Turnitin's current EULA content, or None if it can't be fetched right now.

        Returns:
            Optional[str]: The EULA HTML content, or None on failure.
        """
        try:
            response = get_eula_page(version=resolve_current_eula_version())
        except RequestException:
            log.exception("Failed to fetch the Turnitin EULA content.")
            return None

        if not response.ok:
            log.info(f"Turnitin returned {response.status_code} fetching the EULA content.")
            return None

        return response.text
