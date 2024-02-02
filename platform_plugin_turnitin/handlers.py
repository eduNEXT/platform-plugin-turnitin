"""Event handlers for the Turnitin plugin. """

from platform_plugin_turnitin.tasks import ora_submission_created_task


def ora_submission_created(submission, **kwargs):
    """
    Handle the ORA_SUBMISSION_CREATED event.

    Args:
        submission (ORASubmissionData): The ORA submission data.
    """
    ora_submission_created_task.delay(
        submission.id,
        submission.file_downloads,
    )
