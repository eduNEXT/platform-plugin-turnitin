"""Event handlers for the Turnitin plugin."""

from django.conf import settings

from platform_plugin_turnitin.tasks import ora_submission_created_task
from platform_plugin_turnitin.utils import enabled_in_course


def ora_submission_created(submission, **kwargs):
    """
    Handle the ORA_SUBMISSION_CREATED event.

    If the Turnitin feature is enabled globally or in the course, create a new task to
    send the ORA submission data to Turnitin.

    Args:
        submission (ORASubmissionData): The ORA submission data.
    """
    if settings.ENABLE_TURNITIN_SUBMISSION or enabled_in_course(submission.location):
        ora_submission_created_task.delay(
            submission.uuid,
            submission.anonymous_user_id,
            submission.answer.parts,
            submission.answer.file_names,
            submission.answer.file_urls,
        )
