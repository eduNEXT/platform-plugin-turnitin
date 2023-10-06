"""
Database models for platform_plugin_turnitin.
"""

from django.contrib.auth.models import User
from django.db import models


class TurnitinSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    turnitin_submission_id = models.CharField(max_length=255, blank=True, null=True)
    turnitin_submission_pdf_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission: {self.turnitin_submission_id or 'Not Set'} - created at: {self.created_at}"
