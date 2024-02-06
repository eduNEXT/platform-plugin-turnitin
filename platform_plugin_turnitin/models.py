"""
Database models for platform_plugin_turnitin.
"""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TurnitinSubmission(models.Model):
    """
    Represents a submission to Turnitin.

    Attributes:
    - user (User): The user who made the submission.
    - ora_submission_id (str): The unique identifier for the submission in the Open Response Assessment (ORA) system.
    - turnitin_submission_id (str): The unique identifier for the submission in Turnitin.
    - turnitin_submission_pdf_id (str): The unique identifier for the PDF version of the submission in Turnitin.
    - created_at (datetime): The date and time when the submission was created.

    .. no_pii:
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="turnitin_submissions"
    )
    ora_submission_id = models.CharField(max_length=255, blank=True, null=True)
    turnitin_submission_id = models.CharField(max_length=255, blank=True, null=True)
    turnitin_submission_pdf_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
