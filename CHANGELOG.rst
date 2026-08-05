Change Log
##########

..
   All enhancements and patches to platform_plugin_turnitin will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

Documentation
=============

* Add an "EULA Display and Acceptance" section to the README explaining what the plugin does
  (Turnitin's actual EULA text rendered inline, a required consent checkbox on the ORA
  submission page, backed by a real acceptance check — see Changed, below) and that the Open
  edX Filter it uses is a stock, unmodified ``edx-ora2`` extension point, not a patch. Deploying
  this plugin means the operator is responsible for complying with Turnitin's EULA display
  requirements.

Changed
=======

* **Breaking:** stop accepting the Turnitin EULA on the learner's behalf. Both upload paths (the
  ``upload-file`` REST endpoint and the Celery/ORA event path) now call
  ``TurnitinClient.has_accepted_eula()`` — which checks Turnitin's own
  ``GET /eula/{version}/accept/{user_id}`` record via the previously-unused
  ``get_eula_acceptance_by_user`` handler — before proceeding, and refuse with
  ``451 Unavailable For Legal Reasons`` if there's no record of acceptance. A new
  ``POST .../api/v1/accept-eula/`` endpoint lets the frontend record acceptance explicitly; the
  ``ORASubmissionViewTurnitinWarning`` filter's template now renders a required checkbox that
  calls it before enabling the "Submit" button. Any caller integrating directly against the
  ``upload-file`` endpoint must call ``accept-eula`` first — this is intentionally a breaking
  change to close the compliance gap of assuming consent nobody explicitly gave.
* Render Turnitin's actual EULA text inline on the ORA submission page instead of only linking
  out to it, and resolve the EULA version dynamically via ``GET /eula/latest``
  (``resolve_current_eula_version()`` in ``utils.py``) instead of hardcoding ``v1beta``, used
  consistently for rendering, accepting, and checking acceptance. This means the filter step now
  makes 1-2 additional synchronous outbound calls to Turnitin on every Turnitin-enabled ORA page
  render; each is bounded by ``TURNITIN_API_TIMEOUT`` and fails gracefully (falls back to
  linking out to the EULA) rather than breaking the page, but it's a real added-latency
  tradeoff worth knowing about. The exact response shape of ``GET /eula/latest`` (assumed to
  carry the version under a ``"version"`` key) is inferred, not confirmed against Turnitin's
  documented schema.

Added
=====

* Retry, with a short wait between attempts, the points that previously raised an unrecoverable
  exception (or silently failed) on the first failure: downloading a learner's uploaded file
  from the LMS, checking whether the user has accepted the Turnitin EULA
  (``TurnitinClient.has_accepted_eula()``), and creating the Turnitin submission object itself
  (``TurnitinClient.create_turnitin_submission_object()``, shared by both the Celery/ORA path
  and the direct upload REST endpoint). All three now retry up to ``SUBMISSION_RETRY_ATTEMPTS``
  times (default 3), waiting ``SECONDS_TO_WAIT_BETWEEN_SUBMISSION_RETRIES`` seconds (default 5)
  between attempts, so a transient network blip no longer aborts the whole submission and
  requires a learner to manually resubmit. This does not change the report-generation polling
  loop, add webhooks, or add bulk resubmit — those remain roadmap items.
* Send ``group`` (the ORA assignment's XBlock usage key) and ``group_context`` (its course key)
  in the Create Submission payload's ``metadata``, so submissions can be grouped in Turnitin by
  assignment and course. ``TurnitinClient`` gained optional ``group``/``group_context``
  constructor parameters. Fully populated on the Celery/ORA event path (both values are known
  there); the direct ``upload-file`` REST endpoint only has ``course_id`` available, so it
  sends ``group_context`` but not ``group``.

Changed
=======

* Dropped support for Python 3.8 and Django 3.2/4.0; the plugin now targets Python 3.12 and
  Django 5.2 exclusively. Requirements files were re-compiled under Python 3.12, and CI now
  runs on Python 3.12 / Django 5.2 (``ubuntu-latest``) instead of the old 3.8 matrix.

Fixed
=====

* Default ``TURNITIN_TCA_INTEGRATION_FAMILY`` to ``"Open edX"`` instead of ``None``, so the
  ``X-Turnitin-Integration-Name`` header is meaningful out of the box.
* Default ``TURNITIN_TCA_INTEGRATION_VERSION`` to the ``RELEASE_LINE`` Django setting, falling
  back to ``"turnitin-openedx-platform-plugin <plugin-version>"``, instead of ``None``.
* Apply ``TURNITIN_API_TIMEOUT`` to every ``turnitin_api_handler()`` request, not just the file
  upload branch. Non-upload calls (create submission, get info, generate report, viewer URL,
  EULA) previously had no timeout at all and could hang a Celery worker or web request
  indefinitely.
* URL-encode the uploaded filename (via ``urllib.parse.quote``) before interpolating it into the
  ``Content-Disposition`` header sent to Turnitin. Previously the raw filename was embedded
  unencoded inside the quoted header value, which broke on filenames containing quotes, spaces,
  or non-ASCII characters (e.g. the synthesised ``Student's Text Response Part N.txt`` name, or
  learner-uploaded filenames with accented characters).
* Fix invalid ``"locale": "en-EN"`` sent to the similarity report viewer launch payload; now
  sends the valid ``"en-US"``.
* Change ``submitter_default_permission_set`` from ``"INSTRUCTOR"`` to ``"LEARNER"`` in the
  Create Submission payload. In the ORA flow the learner is both owner and submitter, so
  granting an instructor permission set to the submitter role was inconsistent with who was
  actually being granted it.
* Remove the leading slash in ``get_eula_page()``'s URL prefix, which produced a double slash
  when concatenated with ``turnitin_api_handler()``'s base URL.
* Normalise the user ID to a string (``str(self.user.id)``) everywhere it's sent to Turnitin —
  ``owner``, ``submitter``, ``metadata.owners[].id``, ``metadata.submitter.id``, and
  ``viewer_user_id`` — to match the EULA acceptance payload, which already sent it as a string.
* Enforce ``ALLOWED_FILE_EXTENSIONS`` on the direct ``upload-file`` REST endpoint, which
  previously accepted any file and relied on Turnitin rejecting it with ``UNSUPPORTED_FILETYPE``.
  The check is now shared (``is_allowed_file_extension`` in ``utils.py``) between this endpoint
  and the Celery/ORA event path, which enforced it already.
* Stop hardcoding ``"en-US"`` for the EULA acceptance ``language`` and the viewer launch
  ``locale``. Both now derive from the active Django language (``get_turnitin_locale()`` in
  ``utils.py``), sending ``"es-ES"`` for Spanish — matching the ``es_419``/``es_ES``
  translations this plugin already ships. Only reflects the specific user's preference on the
  direct REST endpoints, where Django's locale middleware has activated it for the request;
  Celery tasks have no active request, so they fall back to the deployment's default
  ``LANGUAGE_CODE`` — still an improvement for Spanish-only deployments, but not fully
  per-learner yet. The ``es-ES`` mapping is a best-effort choice, not confirmed against
  Turnitin's documented locale enum.

0.3.0 - 2024-05-09
**********************************************

Added
=====

* Added setting to enable turnitin integration.
* Added translation for es_419 and es_ES.

0.2.4 - 2024-05-02
**********************************************

Changed
=======

* Remove dependencies section in the README.

0.2.3 - 2024-05-02
**********************************************

Changed
=======

* Update task to use the new event structure.

0.2.2 - 2024-04-24
**********************************************

Changed
=======

* Remove message style for Turnitin warning.

0.2.1 - 2024-04-11
**********************************************

Updated
=======

* Upgrade version of ``openedx-filters`` and ``openedx-events``.

0.2.0 - 2024-02-08
**********************************************

Added
=====

* Add Turnintin API workflow with XBlock.
* Move XBlock implementation to custom turnitin API.
* Receive ORA submission created event.
* Add ORA submission view filter.
* Generate similarity report from celery task.
* Return filename as part of viewer info.
* Add unit tests for the plugin.
* Add documentation for the plugin.

0.1.0 - 2023-07-27
**********************************************

Added
=====

* First release on PyPI.
