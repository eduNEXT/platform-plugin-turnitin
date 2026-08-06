"""This module contains the tasks that will be run by celery."""

import tempfile
from logging import getLogger
from time import sleep
from typing import List
from urllib.parse import urljoin

import requests
from celery import shared_task
from django.conf import settings
from opaque_keys.edx.keys import UsageKey
from rest_framework import status
from rest_framework.response import Response

from platform_plugin_turnitin.api.v1.views import TurnitinClient
from platform_plugin_turnitin.constants import (
    MAX_REQUEST_RETRIES,
    REQUEST_TIMEOUT,
    SECONDS_TO_WAIT_BETWEEN_RETRIES,
    SECONDS_TO_WAIT_BETWEEN_SUBMISSION_RETRIES,
    SUBMISSION_RETRY_ATTEMPTS,
)
from platform_plugin_turnitin.edxapp_wrapper import user_by_anonymous_id
from platform_plugin_turnitin.utils import is_allowed_file_extension

log = getLogger(__name__)


@shared_task
def ora_submission_created_task(
    submission_uuid: str,
    anonymous_user_id: str,
    parts: List[dict],
    file_names: List[str],
    file_urls: List[str],
    block_id: str,
) -> None:
    """
    Task to handle the creation of a new ora submission.

    Args:
        submission_uuid (str): The ORA submission UUID.
        anonymous_user_id (str): The anonymous user ID.
        parts (List[dict]): The parts of the submission with the answers.
        file_names (List[str]): The list of file names.
        file_urls (List[str]): The list of file URLs.
        block_id (str): The XBlock usage key of the ORA assignment.
    """
    user = user_by_anonymous_id(anonymous_user_id)

    send_text_to_turnitin(submission_uuid, user, parts, block_id)
    send_uploaded_files_to_turnitin(submission_uuid, user, file_names, file_urls, block_id)

    check_submission_status_task.apply_async(
        args=[submission_uuid, anonymous_user_id],
        countdown=SECONDS_TO_WAIT_BETWEEN_RETRIES,
    )


@shared_task
def check_submission_status_task(submission_uuid: str, anonymous_user_id: str, attempt: int = 1) -> None:
    """
    Check whether a Turnitin submission is complete, rescheduling itself if not.

    Following Turnitin's documented polling guidance, this does not block a Celery worker with
    a sleep: each run checks once and either generates the report, gives up after
    `MAX_REQUEST_RETRIES` attempts, or reschedules itself `SECONDS_TO_WAIT_BETWEEN_RETRIES`
    seconds later.

    Args:
        submission_uuid (str): The ORA submission UUID.
        anonymous_user_id (str): The anonymous user ID.
        attempt (int): The number of this check, starting at 1.
    """
    user = user_by_anonymous_id(anonymous_user_id)

    if is_submission_complete(submission_uuid, user):
        generate_similarity_report(submission_uuid, user)
        return

    if attempt >= MAX_REQUEST_RETRIES:
        log.info(f"Submission [{submission_uuid}] did not complete after {attempt} checks. Giving up.")
        return

    check_submission_status_task.apply_async(
        args=[submission_uuid, anonymous_user_id],
        kwargs={"attempt": attempt + 1},
        countdown=SECONDS_TO_WAIT_BETWEEN_RETRIES,
    )


def send_text_to_turnitin(ora_submission_uuid: str, user, parts: List[dict], block_id: str) -> None:
    """
    Task to send text to Turnitin.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        parts (List[dict]): The answer of the submission.
        block_id (str): The XBlock usage key of the ORA assignment.
    """
    for idx, part in enumerate(parts, 1):
        text_content = part.get("text").encode("utf-8")
        send_file_to_turnitin(
            ora_submission_uuid, user, text_content, f"Student's Text Response Part {idx}.txt", block_id
        )


def send_uploaded_files_to_turnitin(
    ora_submission_uuid: str, user, file_names: List[str], file_urls: List[str], block_id: str
) -> None:
    """
    Task to send uploaded files to Turnitin.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file_names (List[str]): The list of file names.
        file_urls (List[str]): The list of file URLs.
        block_id (str): The XBlock usage key of the ORA assignment.
    """
    base_url = getattr(settings, "LMS_ROOT_URL", "")

    for file_name, file_url in zip(file_names, file_urls):
        if is_allowed_file_extension(file_name):
            file_link = urljoin(base_url, file_url)
            response = requests.get(file_link, timeout=REQUEST_TIMEOUT)

            for attempt in range(1, SUBMISSION_RETRY_ATTEMPTS):
                if response.ok:
                    break
                log.info(f"Retrying download of file [{file_name}] (attempt {attempt}).")
                sleep(SECONDS_TO_WAIT_BETWEEN_SUBMISSION_RETRIES)
                response = requests.get(file_link, timeout=REQUEST_TIMEOUT)

            if response.ok:
                send_file_to_turnitin(ora_submission_uuid, user, response.content, file_name, block_id)
            else:
                raise Exception(f"Failed to download file from {file_link}")
        else:
            log.info(f"Skipping uploading file [{file_name}] because it has not an allowed extension.")


def send_file_to_turnitin(submission_id: str, user, file_content: bytes, filename: str, block_id: str) -> None:
    """
    Send a file to Turnitin.

    Create a temporary file with the content and upload it to Turnitin
    creating a new submission.

    Args:
        submission_id (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file_content (bytes): The content of the file.
        filename (str): The name of the file.
        block_id (str): The XBlock usage key of the ORA assignment.
    """
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(file_content)
        temp_file.seek(0)
        temp_file.name = filename
        upload_turnitin_submission(submission_id, user, temp_file, block_id)


def upload_turnitin_submission(ora_submission_uuid: str, user, file, block_id: str) -> None:
    """
    Create a new submission in Turnitin.

    The user must have already explicitly accepted the Turnitin EULA (via the accept-eula
    endpoint, called from the ORA submission page) before this runs; it no longer accepts the
    EULA on the user's behalf.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file (File): The file to upload.
        block_id (str): The XBlock usage key of the ORA assignment, sent to Turnitin as the
            submission's `group`, with its course as `group_context`.
    """
    group_context = str(UsageKey.from_string(block_id).course_key)
    turnitin_client = TurnitinClient(user, file, group=block_id, group_context=group_context)

    response = turnitin_client.upload_turnitin_submission_file(ora_submission_uuid)

    if response.status_code == status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS:
        raise Exception(f"Cannot upload submission [{ora_submission_uuid}]: the user has not accepted the EULA.")


def is_submission_complete(ora_submission_uuid: str, user) -> bool:
    """
    Check if the submission is complete.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.

    Returns:
        bool: True if the submission is complete, False otherwise.
    """
    submission_response = get_submission_status(ora_submission_uuid, user)

    if submission_response.status_code != status.HTTP_200_OK:
        return False

    is_complete = all(submission.get("status") in ["COMPLETE", "ERROR"] for submission in submission_response.data)

    if is_complete:
        log.info(f"Submission [{ora_submission_uuid}] is complete.")
        return True

    log.info(f"Submission [{ora_submission_uuid}] is not complete. Checking again...")
    return False


def get_submission_status(ora_submission_uuid: str, user) -> Response:
    """
    Handle the retrieval of the submission information for a Turnitin submission.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.

    Returns:
        Response: The response from the Turnitin API.
    """
    turnitin_client = TurnitinClient(user)
    return turnitin_client.get_submission_status(ora_submission_uuid)


def generate_similarity_report(ora_submission_uuid: str, user) -> None:
    """
    Generate the similarity report for a submission.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
    """
    turnitin_client = TurnitinClient(user)
    turnitin_client.generate_similarity_report(ora_submission_uuid)
