"""Event signals for the Turnitin platform plugin."""

from openedx_events.tooling import OpenEdxPublicSignal

from platform_plugin_turnitin.events.data import ORASubmissionData

# .. event_type: org.openedx.learning.ora.submission.created.v1
# .. event_name: ORA_SUBMISSION_CREATED
# .. event_description: Emitted when a new ORA submission is created
# .. event_data: ORASubmissionData
ORA_SUBMISSION_CREATED = OpenEdxPublicSignal(
    event_type="org.openedx.learning.ora.submission.created.v1",
    data={
        "submission": ORASubmissionData,
    },
)
