"""
Database models for platform_plugin_turnitin.
"""

from django.db import models
from django.contrib.auth.models import User

class TurnitinSubmission(models.Model):
    """
    .. no_pii:
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    turnitin_submission_id = models.CharField(max_length=255, blank=True, null=True)
    turnitin_submission_pdf_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.username} - Turnitin ID: {self.turnitin_submission_id or 'Not Set'}"
