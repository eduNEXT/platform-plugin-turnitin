"""Data classes for Turnitin events."""

from typing import List

import attr


@attr.s(frozen=True)
class ORASubmissionData:
    """
    ORA submission data.
    """

    id: str = attr.ib()
    file_downloads: List[dict] = attr.ib()
