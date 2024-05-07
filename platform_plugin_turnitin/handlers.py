"""Event handlers for the Turnitin plugin."""

from crum import get_current_request
from django.conf import settings
from opaque_keys.edx.keys import CourseKey

from platform_plugin_turnitin.edxapp_wrapper.modulestore import modulestore
from platform_plugin_turnitin.tasks import ora_submission_created_task


def ora_submission_created(submission, **kwargs):  # pylint: disable=unused-argument
    """
    Handle the ORA_SUBMISSION_CREATED event.

    Args:
        submission (ORASubmissionData): The ORA submission data.
    """
    if settings.ENABLE_TURNITIN_SUBMISSION:
        call_ora_submission_created_task(submission)
        return

    course_id = get_current_request().resolver_match.kwargs.get("course_id")
    course_key = CourseKey.from_string(course_id)
    course_block = modulestore().get_course(course_key)
    enable_in_course = course_block.other_course_settings.get("ENABLE_TURNITIN_SUBMISSION", False)

    if enable_in_course:
        call_ora_submission_created_task(submission)


def call_ora_submission_created_task(submission):
    ora_submission_created_task.delay(
        submission.uuid,
        submission.anonymous_user_id,
        submission.answer.parts,
        submission.answer.file_names,
        submission.answer.file_urls,
    )
