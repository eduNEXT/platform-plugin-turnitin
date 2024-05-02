"""Event handlers for the Turnitin plugin."""

from platform_plugin_turnitin.tasks import ora_submission_created_task


def ora_submission_created(submission, **kwargs):
    """
    Handle the ORA_SUBMISSION_CREATED event.

    Args:
        submission (ORASubmissionData): The ORA submission data.
    """
    ora_submission_created_task.delay(
        submission.uuid,
        submission.anonymous_user_id,
        submission.answer.parts,
        submission.answer.file_names,
        submission.answer.file_urls,
    )
