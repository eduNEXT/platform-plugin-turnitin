import json
from typing import Dict, Optional

import requests


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

    # Configuration variables
    TII_API_URL = "https://edunext.tii-sandbox.com"
    TCA_INTEGRATION_FAMILY = "MySweetLMS"
    TCA_INTEGRATION_VERSION = "3.2.4"
    TCA_API_KEY = "[SECRET_KEY]"

    # Headers configuration
    headers = {
        "X-Turnitin-Integration-Name": TCA_INTEGRATION_FAMILY,
        "X-Turnitin-Integration-Version": TCA_INTEGRATION_VERSION,
        "Authorization": f"Bearer {TCA_API_KEY}",
    }

    # Add Content-Type for methods that typically send JSON payload
    if request_method.lower() in ["post", "put", "patch"]:
        headers["Content-Type"] = "application/json"

    if is_upload:
        headers["Content-Type"] = "binary/octet-stream"
        headers["Content-Disposition"] = f'inline; filename="{uploaded_file.name}"'
        response = requests.put(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, data=uploaded_file
        )
        return response

    # Mapping of methods to corresponding functions in the requests library
    method_map = {
        "get": requests.get,
        "post": requests.post,
        "put": requests.put,
        "delete": requests.delete,
        "patch": requests.patch,
    }

    # Retrieving the correct function
    method_func = method_map.get(request_method.lower())

    if not method_func:
        raise ValueError(f"Unsupported request method: {request_method}")

    # Calling the appropriate method
    if request_method.lower() in ["post", "put", "patch"]:
        response = method_func(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, json=data
        )
    else:
        response = method_func(
            f"{TII_API_URL}/api/v1/{url_prefix}", headers=headers, params=data
        )

    return response


def pretty_print_response(response, type_of=""):
    content = response.json()
    print("\n\n")
    print(f"------{type_of}------")
    print("\n\n")
    print(json.dumps(content, indent=4))
    print("\n\n")
    print("------------")
    print("\n\n")


# Returns all the features enabled in Turnitin account.
def get_features_enabled():
    """
    Returns all the features enabled in the Turnitin account.
    """
    response = turnitin_api_handler("get", "features-enabled")
    pretty_print_response(response)


# *---EULA endpoints ---*
# The EULA is a page of terms and conditions that the owner and the
# submiter has to accept in order to send a file to Turnitin.


def get_eula_version_info(version: str = "latest", language: str = "EN"):
    """
    Returns Turnitin's EULA (End User License Agreement) version information.
    The EULA is a page of terms and conditions that both the owner and the submitter
    have to accept in order to send a file to Turnitin.
    """
    response = turnitin_api_handler("get", f"eula/{version}?lang={language}")
    pretty_print_response(response)


def get_eula_page(version: str = "v1beta", language: str = "en-US"):
    """
    Returns the HTML content for a specified EULA version.
    """
    response = turnitin_api_handler("get", f"/eula/{version}/view?lang={language}")
    return response.text


def post_accept_eula_version(payload, version: str = "v1beta"):
    """
    Accepts a specific EULA version.
    This method should be invoked after the user has viewed the EULA content.
    """
    response = turnitin_api_handler("post", f"eula/{version}/accept", payload)
    pretty_print_response(response, "ACCEPT EULA")


def get_eula_acceptance_by_user(user_id):
    """
    Checks if a specific user has accepted a particular EULA version.
    """
    response = turnitin_api_handler("get", f"eula/v1beta/accept/{user_id}")
    pretty_print_response(response)


# *---Submissions endpoints ---*
# Submissions is a Turnithin model that has all relative info to a Assessment send by
# an student.


def post_create_submission(payload):
    """
    Creates a submission object in Turnitin and returns an associated ID.
    This relates to the Turnitin model which contains all information
    related to an assessment sent by a student.
    """
    response = turnitin_api_handler("post", "submissions", payload)
    pretty_print_response(response, "CREATE SUBMISSION")
    return response


def put_upload_submission_file_content(submission_id, file):
    """
    Attaches a document to a student's submission.
    """
    response = turnitin_api_handler(
        "put",
        f"submissions/{submission_id}/original",
        is_upload=True,
        uploaded_file=file,
    )
    pretty_print_response(response, "UPLOAD FILE")
    return response


def get_submission_info(submission_id):
    """
    Fetches all the information related to a specific submission.

    Status:
        CREATED	Submission has been created but no file has been uploaded
        PROCESSING	File contents have been uploaded and the submission is being processed
        COMPLETE	Submission processing is complete
        ERROR	An error occurred during submission processing; see error_code for details

    """
    response = turnitin_api_handler("get", f"submissions/{submission_id}")
    pretty_print_response(response, "SUBMISSION STATUS")
    return response.json()["status"]


def delete_submission(submission_id, is_hard_delete="false"):
    """
    Deletes a submission by its ID.
    The deletion can either be a hard delete or a soft delete based on the parameter provided.
    """
    response = turnitin_api_handler(
        "delete", f"submissions/{submission_id}/?hard={is_hard_delete}"
    )
    pretty_print_response(response)


def put_recover_submission(submission_id):
    """
    Recovers a submission that has been soft deleted
    """
    response = turnitin_api_handler("put", f"submissions/{submission_id}/recover")
    pretty_print_response(response)


# *---Similarity endpoints ---*
# Similarity is a Turnithin report with an internet similarity detection
# score of the student submissions.


def put_generate_similarity_report(submission_id, payload):
    """
    Turnitin begin to process the doc to generate the report.
    """
    response = turnitin_api_handler(
        "put", f"submissions/{submission_id}/similarity", payload
    )
    pretty_print_response(response, "REPORT GENERATION")
    return response


def get_similarity_report_info(submission_id):
    """
    Returns summary information about the requested Similarity Report.
    Status:
        PROCESSING
        COMPLETE
    """
    response = turnitin_api_handler("get", f"submissions/{submission_id}/similarity")
    pretty_print_response(response, "REPORT STATUS")
    return response.json()["status"]


def post_create_viewer_launch_url(submission_id, payload):
    """
    So that users can interact with the details of a submission and Similarity Report,
    Turnitin provides a purpose-built viewer to enable smooth interaction with the
    report details and submitted document.
    """
    response = turnitin_api_handler(
        "post", f"submissions/{submission_id}/viewer-url", payload
    )
    pretty_print_response(response, "URL VIEWER")
    return response.json()["viewer_url"]


def post_generate_similarity_report_pdf(submission_id):
    """
    This endpoint generates Similarty Report pdf and returns an ID that can be used in
    a subsequent API call to download a pdf file.
    """
    response = turnitin_api_handler(
        "post", f"submissions/{submission_id}/similarity/pdf"
    )
    pretty_print_response(response)


def get_similarity_report_pdf(submission_id, pdf_id):
    """
    This endpoint returns the Similarity Report pdf file as stream of bytes.
    """
    response = turnitin_api_handler(
        "get", f"submissions/{submission_id}/similarity/pdf/{pdf_id}"
    )
    pretty_print_response(response)


def get_similarity_report_pdf_status(submission_id, pdf_id):
    """
    This endpoint returns the requested Similarity Report pdf status.
    """
    response = turnitin_api_handler(
        "get", f"submissions/{submission_id}/similarity/pdf/{pdf_id}/status"
    )
    pretty_print_response(response)
