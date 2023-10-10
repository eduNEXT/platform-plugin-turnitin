"""Handler module for Turnitin API integration"""
from .eula import get_eula_acceptance_by_user, get_eula_page, get_eula_version_info, post_accept_eula_version
from .similarity_reports import (
    get_similarity_report_info,
    get_similarity_report_pdf,
    get_similarity_report_pdf_status,
    post_create_viewer_launch_url,
    post_generate_similarity_report_pdf,
    put_generate_similarity_report,
)
from .submissions import (
    delete_submission,
    get_submission_info,
    post_create_submission,
    put_recover_submission,
    put_upload_submission_file_content,
)
