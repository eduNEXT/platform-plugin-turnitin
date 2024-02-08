"""Utility functions for the Turnitin API."""

from typing import Optional, Tuple

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.response import Response

from platform_plugin_turnitin.edxapp_wrapper import CourseInstructorRole, CourseStaffRole, get_course_overview_or_none


def get_fullname(name: str) -> Tuple[str, str]:
    """
    Returns the first and last name from a full name.

    Args:
        name (str): Full name.

    Returns:
        Tuple[str, str]: First and last name.
    """
    first_name, last_name = "", ""

    if name:
        fullname = name.split(" ", 1)
        first_name = fullname[0]

        if fullname[1:]:
            last_name = fullname[1]

    return first_name, last_name


def api_field_errors(field_errors: dict, status_code: int) -> Response:
    """
    Build a response with field errors.

    Args:
        field_errors (dict): Errors to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with field errors.
    """
    return Response(data={"field_errors": field_errors}, status=status_code)


def api_error(error: str, status_code: int) -> Response:
    """
    Build a response with an error.

    Args:
        error (str): Error to return.
        status_code (int): Status code to return.

    Returns:
        Response: Response with an error.
    """
    return Response(data={"error": error}, status=status_code)


def validate_request(
    request, course_id: str, only_course: bool = False
) -> Optional[Response]:
    """
    Validate the request and return a error response if the request is invalid.

    Error responses are returned if:
    - The course ID is invalid.
    - The course is not found.
    - The user does not have access to consume the endpoint

    Args:
        request (Request): The request object.
        course_id (str): The course ID.
        only_course (bool, optional): If True, only validate the course ID. Defaults to False.

    Returns:
        Optional[Response]: A response object if the request is invalid.
    """
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        return api_field_errors(
            {"course_id": f"The supplied {course_id=} key is not valid."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    course_overview = get_course_overview_or_none(course_id)

    if course_overview is None:
        return api_field_errors(
            {"course_id": f"The course with {course_id=} is not found."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if only_course:
        return None

    user_has_access = any(
        [
            request.user.is_staff,
            CourseStaffRole(course_key).has_user(request.user),
            CourseInstructorRole(course_key).has_user(request.user),
        ]
    )

    if not user_has_access:
        return api_error(
            "The user does not have access to consume the endpoint.",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return None
