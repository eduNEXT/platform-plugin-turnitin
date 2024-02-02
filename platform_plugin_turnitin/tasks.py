"""This file contains the tasks that will be run by celery."""

import tempfile
from urllib.parse import urljoin

import requests

from celery import shared_task
from django.conf import settings
from rest_framework import status
from submissions import api as submissions_api

from platform_plugin_turnitin.api.v1.views import TurnitinClient
from platform_plugin_turnitin.edxapp_wrapper import user_by_anonymous_id


@shared_task
def ora_submission_created_task(submission_id: str, file_downloads: list) -> None:
    """
    Task to handle the creation of a new ora submission.

    Args:
        submission_id (str): The ORA submission ID.
        file_downloads (list): The list of file downloads.
    """
    print(f"\n\nORA Submission ID: {submission_id}\n\n")

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
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(part.get("text").encode("utf-8"))
            temp_file.seek(0)
            temp_file.name = "response.txt"
            upload_turnitin_submission(submission_id, user, temp_file)


def send_uploaded_files_to_turnitin(
    submission_id: str, user, file_downloads: list
) -> None:
    """
    Task to send uploaded files to Turnitin.

    Args:
        submission_id (str): The ORA submission ID.
        user (User): The user who made the submission.
        file_downloads (list): The list of file downloads.
    """
    base_url = getattr(settings, "LMS_ROOT_URL", "")

    for file in file_downloads:
        file_link = urljoin(base_url, file.get("download_url"))
        response = requests.get(file_link, timeout=5)

        if response.status_code == status.HTTP_200_OK:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(response.content)
                temp_file.seek(0)
                temp_file.name = file.get("name")
                upload_turnitin_submission(submission_id, user, temp_file)
        else:
            raise Exception(f"Failed to download file from {file_link}")


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

    if agreement_response.status_code != status.HTTP_200_OK:
        raise Exception("Failed to accept the EULA agreement.")

    turnitin_client.upload_turnitin_submission_file(submission_id)
