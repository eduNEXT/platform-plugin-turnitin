Platform Plugin Turnitin
########################

|ci-badge| |license-badge| |status-badge|


Purpose
*******

Open edX plugin that includes an API to integrate with Turnitin. This plugin
allows to learners to upload files to Turnitin and instructors to get
information about the submissions, generate similarity reports, and get the
viewer URL of the submissions. This plugin is designed to be used with the `Open
Response Assessment (ORA)`_ XBlock of the Open edX platform.

This plugin has been created as an open source contribution to the Open edX
platform and has been funded by the Unidigital project from the Spanish
Government - 2024.

.. _Open Response Assessment (ORA): https://github.com/openedx/edx-ora2


Dependencies
************

This plugin depends the next libraries. Currently, the versions that are
compatible with this plugin are the next:

- Open edX Events with `these commits <https://github.com/openedx/openedx-events/compare/main...eduNEXT:openedx-events:9.4.0/edues>`__
- Open edX Filters with `these commits <https://github.com/openedx/openedx-filters/compare/main...eduNEXT:openedx-filters:1.6.0/edues>`__
- ORA2 XBlock with `these commits <https://github.com/openedx/edx-ora2/compare/master...eduNEXT:edx-ora2:6.0.31/edues>`__

The dependecies with these commits are temporary. We are working
to include these changes in master.


Getting Started
***************

Developing
==========

One Time Setup
--------------

Clone the repository:

.. code-block:: bash

  git clone git@github.com:eduNEXT/platform_plugin_turnitin.git
  cd platform_plugin_turnitin

Set up a virtualenv with the same name as the repo and activate it. Here's how
you might do that if you have ``virtualenv`` set up:

.. code-block:: bash

  virtualenv -p python3.8 platform_plugin_turnitin

Every time you develop something in this repo
---------------------------------------------

Activate the virtualenv. Here's how you might do that if you're using
``virtualenv``:

.. code-block:: bash

  source platform_plugin_turnitin/bin/activate

Grab the latest code:

.. code-block:: bash

  git checkout main
  git pull

Install/update the dev requirements:

.. code-block:: bash

  make requirements

Run the tests and quality checks (to verify the status before you make any
changes):

.. code-block:: bash

  make validate

Make a new branch for your changes:

.. code-block:: bash

  git checkout -b <your_github_username>/<short_description>

Using your favorite editor, edit the code to make your change:

.. code-block:: bash

  vim ...

Run your new tests:

.. code-block:: bash

  pytest ./path/to/new/tests

Run all the tests and quality checks:

.. code-block:: bash

  make validate

Commit all your changes, push your branch to github, and open a PR:

.. code-block:: bash

  git commit ...
  git push


Using the API
*************

**IMPORTANT**: To use the API, you need to configure the Turnitin credentials.
More information about this in the `next section`_

The API is protected with the same auth method as the Open edX platform.
For generate a token, you can use the next endpoint:

- POST ``<lms_host>/oauth2/access_token/``: Generate a token for the user. The
  content type of the request must be ``application/x-www-form-urlencoded``.

  **Body parameters**

  - ``client_id``: Client ID of the OAuth2 application. You can find it in the
    Django admin panel. Normally, it is ``login-service-client-id``.
  - ``grant_type``: Grant type of the OAuth2 application. Normally, it is
    ``password``.
  - ``username``: Username of the user.
  - ``password``: Password of the user.
  - ``token_type``: Type of the token. By default, it is ``bearer``

  Alternatively, you can use a new OAuth2 application. You can create a new
  application in the Django admin panel. The body parameters are the same as
  the previous endpoint, but you must use the ``client_id`` and ``client_secret``
  of the new application. The ``grant_type`` must be ``client_credentials``.

  **Response**

  - ``access_token``: Access token of the user. You must use this token in the
    ``Authorization`` header of the requests to the API.

Then, you are ready to use the API. The next endpoints are available:

Learners endpoints
==================

- POST ``<lms_host>/platform-plugin-turnitin/<course_id>/api/v1/upload-file/<ora_submission_id>/``:
  Upload a file to Turnitin.

  **Path parameters**

  - ``course_id``: ID of the course.
  - ``ora_submission_id``: ID of the ORA submission.

  **Body parameters**

  - ``file``: File to upload.

Instructors endpoints
=====================

- GET ``<lms_host>/platform-plugin-turnitin/<course_id>/api/v1/submission/<ora_submission_id>/``:
  Get the Turnitin submissions of an ORA submission.

  **Path parameters**

  - ``course_id``: ID of the course.
  - ``ora_submission_id``: ID of the ORA submission.

- PUT ``<lms_host>/platform-plugin-turnitin/<course_id>/api/v1/similarity-report/<ora_submission_id>/``:
  Generate a similarity report of the Turnitin submissions of an ORA submission.

  **Path parameters**

  - ``course_id``: ID of the course.
  - ``ora_submission_id``: ID of the ORA submission.

- GET ``<lms_host>/platform-plugin-turnitin/<course_id>/api/v1/similarity-report/<ora_submission_id>/``:
  Get the similarity report of the Turnitin submissions of an ORA submission.

  **Path parameters**

  - ``course_id``: ID of the course.
  - ``ora_submission_id``: ID of the ORA submission.

- GET ``<lms_host>/platform-plugin-turnitin/<course_id>/api/v1/viewer-url/<ora_submission_id>/``:
  Get the viewer URL of the Turnitin submissions of an ORA submission.

  **Path parameters**

  - ``course_id``: ID of the course.
  - ``ora_submission_id``: ID of the ORA submission.

.. _next section: #configuring-required-in-the-open-edx-platform

Configuring required in the Open edX platform
*********************************************

You need to configure the following settings to use the plugin:

.. code-block:: python

  TURNITIN_TII_API_URL = "<YOUR-API-URL>"
  TURNITIN_TCA_API_KEY = "<YOUR-API-KEY>"
  TURNITIN_TCA_INTEGRATION_FAMILY = "MySweetLMS"
  TURNITIN_TCA_INTEGRATION_VERSION = "3.2.4"


Getting Help
************

If you're having trouble, we have discussion forums at `discussions`_ where you
can connect with others in the community.

Our real-time conversations are on Slack. You can request a
`Slack invitation`_, then join our `community Slack workspace`_.

For anything non-trivial, the best path is to open an `issue`_ in this
repository with as many details about the issue you are facing as you
can provide.

For more information about these options, see the `Getting Help`_ page.

.. _discussions: https://discuss.openedx.org
.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/
.. _issue: https://github.com/eduNEXT/platform-plugin-turnitin/issues
.. _Getting Help: https://openedx.org/getting-help


License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.


Contributing
************

Contributions are very welcome. Please read `How To Contribute`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

.. _How To Contribute: https://openedx.org/r/how-to-contribute


Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@edunext.co.

.. It's not required by our contractor at the moment but can be published later
.. .. |pypi-badge| image:: https://img.shields.io/pypi/v/platform-plugin-turnitin.svg
    :target: https://pypi.python.org/pypi/platform-plugin-turnitin/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/eduNEXT/platform-plugin-turnitin/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/eduNEXT/platform-plugin-turnitin/actions
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/platform-plugin-turnitin.svg
    :target: https://github.com/eduNEXT/platform-plugin-turnitin/blob/main/LICENSE.txt
    :alt: License

..  |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
