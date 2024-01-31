"""
EULA handlers for turnitin plugin
"""

from .api_handler import turnitin_api_handler


def get_eula_version_info(version: str = "latest", language: str = "EN"):
    """
    Returns Turnitin's EULA (End User License Agreement) version information.
    The EULA is a page of terms and conditions that both the owner and the submitter
    have to accept in order to send a file to Turnitin.
    """
    response = turnitin_api_handler("get", f"eula/{version}?lang={language}")
    return response


def get_eula_page(version: str = "v1beta", language: str = "en-US"):
    """
    Returns the HTML content for a specified EULA version.
    """
    response = turnitin_api_handler("get", f"/eula/{version}/view?lang={language}")
    return response


def post_accept_eula_version(payload, version: str = "v1beta"):
    """
    Accepts a specific EULA version.
    This method should be invoked after the user has viewed the EULA content.
    """
    response = turnitin_api_handler("post", f"eula/{version}/accept", payload)
    return response


def get_eula_acceptance_by_user(user_id):
    """
    Checks if a specific user has accepted a particular EULA version.
    """
    response = turnitin_api_handler("get", f"eula/v1beta/accept/{user_id}")
    return response
