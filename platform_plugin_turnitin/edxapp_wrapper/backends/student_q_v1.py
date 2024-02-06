"""
Student definitions for Open edX Quince release.
"""

from common.djangoapps.student.models.user import user_by_anonymous_id  # pylint: disable=import-error, unused-import
from common.djangoapps.student.roles import (  # pylint: disable=import-error, unused-import
    CourseInstructorRole,
    CourseStaffRole,
)
