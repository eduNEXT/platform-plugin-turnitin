"""
Student generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_course_instructor_role():
    """
    Wrapper for `CourseInstructorRole` in edx-platform.
    """
    backend_function = settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.CourseInstructorRole


def get_course_staff_role():
    """
    Wrapper for `CourseStaffRole` in edx-platform.
    """
    backend_function = settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.CourseStaffRole


def user_by_anonymous_id(*args, **kwargs):
    """
    Wrapper method of `user_by_anonymous_id` in edx-platform.
    """
    backend_function = settings.PLATFORM_PLUGIN_TURNITIN_STUDENT_BACKEND
    backend = import_module(backend_function)

    return backend.user_by_anonymous_id(*args, **kwargs)


CourseInstructorRole = get_course_instructor_role()
CourseStaffRole = get_course_staff_role()
