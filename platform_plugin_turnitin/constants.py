"""This module contains constants used in the Turnitin plugin."""

ALLOWED_FILE_EXTENSIONS = ["doc", "docx", "pdf", "txt"]
MAX_REQUEST_RETRIES = 25
# Turnitin's documented polling guidance: don't poll Get Submission Info until 30 minutes
# after upload, then every 30 minutes after that.
SECONDS_TO_WAIT_BETWEEN_RETRIES = 1800
REQUEST_TIMEOUT = 5
SUBMISSION_RETRY_ATTEMPTS = 3
SECONDS_TO_WAIT_BETWEEN_SUBMISSION_RETRIES = 5
