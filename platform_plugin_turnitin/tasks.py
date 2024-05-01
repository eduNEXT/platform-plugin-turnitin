"""This module contains the tasks that will be run by celery."""

import tempfile
from logging import getLogger
from time import sleep
from typing import List
from urllib.parse import urljoin

import requests
from celery import shared_task
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from platform_plugin_turnitin.api.v1.views import TurnitinClient
from platform_plugin_turnitin.constants import (
    ALLOWED_FILE_EXTENSIONS,
    MAX_REQUEST_RETRIES,
    REQUEST_TIMEOUT,
    SECONDS_TO_WAIT_BETWEEN_RETRIES,
)
from platform_plugin_turnitin.edxapp_wrapper import user_by_anonymous_id

log = getLogger(__name__)


@shared_task
def ora_submission_created_task(
    submission_uuid: str,
    anonymous_user_id: str,
    parts: List[dict],
    file_names: List[str],
    file_urls: List[str],
) -> None:
    """
    Task to handle the creation of a new ora submission.

    Args:
        submission_uuid (str): The ORA submission UUID.
        anonymous_user_id (str): The anonymous user ID.
        parts (dict): The parts of the submission with the answers.
        file_names (List[str]): The list of file names.
        file_urls (List[str]): The list of file URLs.
    """
    user = user_by_anonymous_id(anonymous_user_id)

    send_text_to_turnitin(submission_uuid, user, parts)
    send_uploaded_files_to_turnitin(submission_uuid, user, file_names, file_urls)

    for _ in range(MAX_REQUEST_RETRIES):
        if is_submission_complete(submission_uuid, user):
            generate_similarity_report(submission_uuid, user)
            break
        sleep(SECONDS_TO_WAIT_BETWEEN_RETRIES)


def send_text_to_turnitin(ora_submission_uuid: str, user, parts: List[dict]) -> None:
    """
    Task to send text to Turnitin.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        parts (List[dict]): The answer of the submission.
    """
    for part in parts:
        text_content = part.get("text").encode("utf-8")
        send_file_to_turnitin(ora_submission_uuid, user, text_content, "Students' Text Response.txt")


def send_uploaded_files_to_turnitin(
    ora_submission_uuid: str, user, file_names: List[str], file_urls: List[str]
) -> None:
    """
    Task to send uploaded files to Turnitin.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file_names (List[str]): The list of file names.
        file_urls (List[str]): The list of file URLs.
    """
    base_url = getattr(settings, "LMS_ROOT_URL", "")

    for file_name, file_url in zip(file_names, file_urls):
        file_extension = file_name.split(".")[-1]

        if file_extension in ALLOWED_FILE_EXTENSIONS:
            file_link = urljoin(base_url, file_url)
            response = requests.get(file_link, timeout=REQUEST_TIMEOUT)

            if response.ok:
                send_file_to_turnitin(ora_submission_uuid, user, response.content, file_name)
            else:
                raise Exception(f"Failed to download file from {file_link}")
        else:
            log.info(f"Skipping uploading file [{file_name}] because it has not an allowed extension.")


def send_file_to_turnitin(submission_id: str, user, file_content: bytes, filename: str) -> None:
    """
    Send a file to Turnitin.

    Create a temporary file with the content and upload it to Turnitin
    creating a new submission.

    Args:
        submission_id (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file_content (bytes): The content of the file.
        filename (str): The name of the file.
    """
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(file_content)
        temp_file.seek(0)
        temp_file.name = filename
        upload_turnitin_submission(submission_id, user, temp_file)


def upload_turnitin_submission(ora_submission_uuid: str, user, file) -> None:
    """
    Create a new submission in Turnitin.

    First, the user must accept the EULA agreement. Then, the file is uploaded to Turnitin.

    Args:
        ora_submission_uuid (str): The ORA submission UUID.
        user (User): The user who made the submission.
        file (File): The file to upload.
    """
    turnitin_client = TurnitinClient(user, file)

    agreement_response = turnitin_client.accept_eula_agreement()

    if not agreement_response.ok:
        raise Exception("Failed to accept the EULA agreement.")

    turnitin_client.upload_turnitin_submission_file(ora_submission_uuid)


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
