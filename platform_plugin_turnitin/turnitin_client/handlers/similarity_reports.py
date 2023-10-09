from .api_handler import turnitin_api_handler
from .utils import pretty_print_response


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
    return response


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
    return response


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
