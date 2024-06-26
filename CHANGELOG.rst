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

*

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
