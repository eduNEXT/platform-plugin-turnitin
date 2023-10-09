from typing import Dict, Optional

import requests
from django.conf import settings

from .utils import pretty_print_response

TII_API_URL = getattr(settings, "TURNITIN_TII_API_URL", None)
TCA_INTEGRATION_FAMILY = getattr(settings, "TURNITIN_TCA_INTEGRATION_FAMILY", None)
TCA_INTEGRATION_VERSION = getattr(settings, "TURNITIN_TCA_INTEGRATION_VERSION", None)
TCA_API_KEY = getattr(settings, "TURNITIN_TCA_API_KEY", None)


def turnitin_api_handler(
    request_method: str,
    url_prefix: str = "",
    data: Optional[Dict] = None,
    is_upload: bool = False,
    uploaded_file=None,
):
    """
    Handles API requests to the Turnitin service.

    Parameters:
    - request_method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'PATCH', 'DELETE').
    - data (dict): The payload to be sent in the request. Use None for methods that don't require a payload.
    - url_prefix (str): The endpoint suffix for the API URL.

    Returns:
    - Response: A requests.Response object containing the server's response to the request.

    Raises:
    - ValueError: If an unsupported request method is provided.
    """
    headers = {
        "X-Turnitin-Integration-Name": TCA_INTEGRATION_FAMILY,
        "X-Turnitin-Integration-Version": TCA_INTEGRATION_VERSION,
        "Authorization": f"Bearer {TCA_API_KEY}",
    }

    if request_method.lower() in ["post", "put", "patch"]:
        headers["Content-Type"] = "application/json"

    if is_upload:
        headers["Content-Type"] = "binary/octet-stream"
        headers["Content-Disposition"] = f'inline; filename="{uploaded_file.name}"'
        response = requests.put(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, data=uploaded_file
        )
        return response

    method_map = {
        "get": requests.get,
        "post": requests.post,
        "put": requests.put,
        "delete": requests.delete,
        "patch": requests.patch,
    }

    method_func = method_map.get(request_method.lower())

    if not method_func:
        raise ValueError(f"Unsupported request method: {request_method}")

    if request_method.lower() in ["post", "put", "patch"]:
        response = method_func(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, json=data
        )
    else:
        response = method_func(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, params=data
        )

    return response


def get_features_enabled():
    """
    Returns all the features enabled in the Turnitin account.
    """
    response = turnitin_api_handler("get", "features-enabled")
    pretty_print_response(response)
