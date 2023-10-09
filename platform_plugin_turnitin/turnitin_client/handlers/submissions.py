from .api_handler import turnitin_api_handler
from .utils import pretty_print_response


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
    return response


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
