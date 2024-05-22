Platform Plugin Turnitin
########################

|ci-badge| |license-badge| |status-badge|


Purpose
*******

Open edX plugin that includes an API to integrate with Turnitin. This plugin
allows to learners to upload files to Turnitin and instructors to get
information about the submissions, generate similarity reports, and get the
viewer URL of the submissions. This plugin is designed to be used with the
`Open Response Assessment (ORA)`_ XBlock of the Open edX platform.

This plugin has been created as an open source contribution to the Open edX
platform and has been funded by the Unidigital project from the Spanish
Government - 2024.

.. _Open Response Assessment (ORA): https://github.com/openedx/edx-ora2

**NOTE**: This plugin only includes the API to interact with Turnitin. All
frontend changes that are related to displaying the similarity reports to
instructors are included in the `ORA Grading MFE`_.

.. _ORA Grading MFE: https://github.com/eduNEXT/frontend-app-ora-grading/pull/4

Compatibility Notes
===================

+------------------+--------------+
| Open edX Release | Version      |
+==================+==============+
| Palm             | >= 0.2.0     |
+------------------+--------------+
| Quince           | >= 0.2.0     |
+------------------+--------------+
| Redwood          | >= 0.2.0     |
+------------------+--------------+

The settings can be changed in ``platform_plugin_turnitin/settings/common.py``
or, for example, in tutor configurations.

**NOTE**: the current ``common.py`` works with Open edX Palm, Quince and
Redwood version.


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

Deploying
==========

Tutor environments
------------------

To use this plugin in a Tutor environment, you must install it as a requirement of the ``openedx`` image. To achieve this, follow these steps:

.. code-block:: bash

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edunext/platform-plugin-turnitin@vX.Y.Z
    tutor images build openedx

Then, deploy the resultant image in your environment.

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

By default the turnitin functionality is disabled. If you want to enable the
functionality globally (in all courses) add the following setting in your LMS:

.. code-block:: python

  ENABLE_TURNITIN_SUBMISSION = True

Optionally, you can enable the functionality in a specific course by adding the
following setting from **Studio** > **Advanced Settings** > **Other Course
Settings**:

.. code-block:: json

  {
    "ENABLE_TURNITIN_SUBMISSION": true
  }

Next, you must include the following setting to enable the filter that will
display the warning message to the learner about Turnitin:

.. code-block:: python

  OPEN_EDX_FILTERS_CONFIG = {
    "org.openedx.learning.ora.submission_view.render.started.v1": {
      "fail_silently": False,
      "pipeline": [
        "platform_plugin_turnitin.extensions.filters.ORASubmissionViewTurnitinWarning",
      ]
    },
  }

Finally, to use the turnitin API it is necessary to configure the following
settings in your LMS:

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

Translations
============

This plugin is initially available in English and Spanish. You can help by
translating this component to other languages. Follow the steps below:

1. Run the following command to extract the strings from the code and create
   the ``.po`` file specifying the locale, eg: ``fr_FR``:

   .. code-block:: bash

      cd platform_plugin_turnitin && django-admin makemessages -l fr_FR -v1 -d django
2. Update the ``.po`` file with the translations.
3. Run ``make compile_translations``, this will generate the ``.mo`` file.
4. Create a pull request with your changes.


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
