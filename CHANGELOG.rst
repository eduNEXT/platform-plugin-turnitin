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
