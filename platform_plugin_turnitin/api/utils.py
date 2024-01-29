"""Utility functions for the Turnitin API."""

from typing import Tuple

from rest_framework.response import Response


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
