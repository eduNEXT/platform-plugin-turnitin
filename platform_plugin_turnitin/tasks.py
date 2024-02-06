"""This module contains the tasks that will be run by celery."""

import tempfile
from logging import getLogger
from typing import List
from urllib.parse import urljoin

import requests
from celery import shared_task
from django.conf import settings
from submissions import api as submissions_api

from platform_plugin_turnitin.api.v1.views import TurnitinClient
from platform_plugin_turnitin.constants import ALLOWED_FILE_EXTENSIONS
from platform_plugin_turnitin.edxapp_wrapper import user_by_anonymous_id

log = getLogger(__name__)


@shared_task
def ora_submission_created_task(submission_id: str, file_downloads: List[dict]) -> None:
    """
    Task to handle the creation of a new ora submission.

    Args:
        submission_id (str): The ORA submission ID.
        file_downloads (List[dict]): The list of file downloads.
    """
    submission_data = dict(submissions_api.get_submission_and_student(submission_id))
    user = user_by_anonymous_id(submission_data["student_item"]["student_id"])

    send_text_to_turnitin(submission_id, user, submission_data["answer"])
    send_uploaded_files_to_turnitin(submission_id, user, file_downloads)


def send_text_to_turnitin(submission_id: str, user, answer: dict) -> None:
    """
    Task to send text to Turnitin.

    Args:
        submission_id (str): The ORA submission ID.
        user (User): The user who made the submission.
        answer (dict): The answer of the submission.
    """
    for part in answer["parts"]:
        text_content = part.get("text").encode("utf-8")
        send_file_to_turnitin(submission_id, user, text_content, "response.txt")


def send_uploaded_files_to_turnitin(
    submission_id: str, user, file_downloads: List[dict]
) -> None:
    """
    Task to send uploaded files to Turnitin.

    Args:
        submission_id (str): The ORA submission ID.
        user (User): The user who made the submission.
        file_downloads (List[dict]): The list of file downloads.
    """
    base_url = getattr(settings, "LMS_ROOT_URL", "")

    for file in file_downloads:
        filename = file.get("name", "")
        file_extension = filename.split(".")[-1]
        if file_extension in ALLOWED_FILE_EXTENSIONS:
            file_link = urljoin(base_url, file.get("download_url"))
            response = requests.get(file_link, timeout=5)

            if response.ok:
                send_file_to_turnitin(submission_id, user, response.content, filename)
            else:
                raise Exception(f"Failed to download file from {file_link}")
        else:
            log.info(
                f"Skipping uploading file [{filename}] because it has not an allowed extension."
            )


def send_file_to_turnitin(
    submission_id: str, user, file_content: bytes, filename: str
) -> None:
    """
    Send a file to Turnitin.

    Create a temporary file with the content and upload it to Turnitin
    creating a new submission.

    Args:
        submission_id (str): The ORA submission ID.
        user (User): The user who made the submission.
        file_content (bytes): The content of the file.
        filename (str): The name of the file.
    """
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(file_content)
        temp_file.seek(0)
        temp_file.name = filename
        upload_turnitin_submission(submission_id, user, temp_file)


def upload_turnitin_submission(submission_id: str, user, file) -> None:
    """
    Create a new submission in Turnitin.

    First, the user must accept the EULA agreement. Then, the file is uploaded to Turnitin.

    Args:
        submission_id (str): The ORA submission ID.
        user (User): The user who made the submission.
        file (File): The file to upload.
    """
    turnitin_client = TurnitinClient(user, file)

    agreement_response = turnitin_client.accept_eula_agreement()

    if not agreement_response.ok:
        raise Exception("Failed to accept the EULA agreement.")

    turnitin_client.upload_turnitin_submission_file(submission_id)
