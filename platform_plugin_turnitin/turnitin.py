"""TO-DO: Write a description of what this XBlock is."""

import json
from datetime import datetime

import pkg_resources
from django.contrib.auth.models import User
from django.utils import translation
from webob import Response
from xblock.core import XBlock
from xblock.fields import Integer, Scope
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader

from platform_plugin_turnitin.turnitin_client.handlers import (
    get_eula_page,
    get_similarity_report_info,
    get_submission_info,
    post_accept_eula_version,
    post_create_submission,
    post_create_viewer_launch_url,
    put_generate_similarity_report,
    put_upload_submission_file_content,
)

from .models import TurnitinSubmission


@XBlock.needs("user")
@XBlock.needs("user_state")
class TurnitinXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def studio_view(self, context=None):
        """
        The primary view of the TurnitinXBlock, shown to students
        when viewing courses.
        """
        if context:
            pass  # TO-DO: do something based on the context.
        html = self.resource_string("static/html/cms.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/turnitin.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string("static/js/src/turnitin.js"))
        frag.initialize_js("TurnitinXBlock")
        return frag

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TurnitinXBlock, shown to students
        when viewing courses.
        """
        if context:
            pass  # TO-DO: do something based on the context.
        html = self.resource_string("static/html/turnitin.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/turnitin.css"))

        # Add i18n js
        statici18n_js_url = self._get_statici18n_js_url()
        if statici18n_js_url:
            frag.add_javascript_url(
                self.runtime.local_resource_url(self, statici18n_js_url)
            )

        frag.add_javascript(self.resource_string("static/js/src/turnitin.js"))
        frag.initialize_js("TurnitinXBlock")
        return frag

    # ----------------------------------------------------------------------------
    def get_user_data(self):
        """
        Fetches user-related data, including user ID, email, and name.

        Returns:
            dict: A dictionary containing user ID, email, and name.
        """
        user_service = self.runtime.service(self, "user")
        current_user = user_service.get_current_user()
        return {
            "user_id": current_user.opt_attrs["edx-platform.user_id"],
            "user_email": current_user.emails[0],
            "user_name": current_user.full_name.split(),
        }

    @XBlock.json_handler
    def get_eula_agreement(self, data, suffix=""):
        """
        Fetches the End User License Agreement (EULA) content.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: A dictionary containing the HTML content of the EULA and the status code.
        """
        response = get_eula_page()
        return {"html": response.text, "status": response.status_code}

    @XBlock.json_handler
    def accept_eula_agreement(self, data, suffix=""):
        """
        Submits acceptance of the EULA for the current user.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: The response after accepting the EULA.
        """
        user_id = self.get_user_data()["user_id"]
        date_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = {
            "user_id": str(user_id),
            "accepted_timestamp": date_now,
            "language": "en-US",
        }
        response = post_accept_eula_version(payload)
        return response.json()

    def create_turnitin_submission_object(self):
        """
        Constructs a Turnitin submission object based on the user's data.

        Returns:
            Response: The response from the Turnitin submission API.
        """
        user_data = self.get_user_data()
        user_name = user_data["user_name"]
        date_now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        payload = {
            "owner": user_data["user_id"],
            "title": self.location.block_id,
            "submitter": user_data["user_id"],
            "owner_default_permission_set": "LEARNER",
            "submitter_default_permission_set": "INSTRUCTOR",
            "extract_text_only": False,
            "metadata": {
                "owners": [
                    {
                        "id": user_data["user_id"],
                        "given_name": user_name[0] if user_name else "no_name",
                        "family_name": " ".join(user_name[1:])
                        if len(user_name) > 1
                        else "no_last_name",
                        "email": user_data["user_email"],
                    }
                ],
                "submitter": {
                    "id": user_data["user_id"],
                    "given_name": user_name[0] if user_name else "no_name",
                    "family_name": " ".join(user_name[1:])
                    if len(user_name) > 1
                    else "no_last_name",
                    "email": user_data["user_email"],
                },
                "original_submitted_time": date_now,
            },
        }
        return post_create_submission(payload)

    @XBlock.handler
    def upload_turnitin_submission_file(self, data, suffix=""):
        """
        Handles the upload of the user's file to Turnitin.

        Args:
            data (WebRequest): Web request containing the file to be uploaded.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            Response: The response after uploading the file to Turnitin.
        """
        turnitin_submission = self.create_turnitin_submission_object()
        if turnitin_submission.status_code == 201:
            turnitin_submission_id = turnitin_submission.json()["id"]
            current_user_id = self.get_user_data()["user_id"]
            current_user = User.objects.get(id=current_user_id)
            submission = TurnitinSubmission(
                user=current_user, turnitin_submission_id=turnitin_submission_id
            )
            submission.save()
            myfile = data.params["myfile"].file
            # turnitin_submission_id='0a966646-83f9-4ce6-aa47-71e07baf4e30'
            response = put_upload_submission_file_content(
                turnitin_submission_id, myfile
            )
            return Response(
                json.dumps(response.json()),
                content_type="application/json",
                charset="UTF-8",
            )
        return Response(
            json.dumps(turnitin_submission.json()),
            content_type="application/json",
            charset="UTF-8",
        )

    @XBlock.json_handler
    def get_submission_status(self, data, suffix=""):
        """
        Retrieves the status of the latest Turnitin submission for the user.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: Information related to the user's latest Turnitin submission.
        """
        current_user_id = self.get_user_data()["user_id"]
        current_user = User.objects.get(id=current_user_id)
        try:
            last_submission = TurnitinSubmission.objects.filter(
                user=current_user
            ).latest("created_at")
        except TurnitinSubmission.DoesNotExist:
            return {"success": False}
        # last_submission = 'de6784c5-471f-4220-aff1-16b6b44dffcf'
        response = get_submission_info(last_submission.turnitin_submission_id)
        return response.json()

    @XBlock.json_handler
    def generate_similarity_report(self, data, suffix=""):
        """
        Initiates the generation of a similarity report for the user's latest Turnitin submission.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: The status of the similarity report generation process.
        """

        payload = {
            "indexing_settings": {"add_to_index": True},
            "generation_settings": {
                "search_repositories": [
                    "INTERNET",
                    "SUBMITTED_WORK",
                    "PUBLICATION",
                    "CROSSREF",
                    "CROSSREF_POSTED_CONTENT",
                ],
                "submission_auto_excludes": [
                    "b84b77d1-da0f-4f45-b002-8aec4f4796d6",
                    "b86de142-bc44-4f95-8467-84af12b89217",
                ],
                "auto_exclude_self_matching_scope": "ALL",
                "priority": "HIGH",
            },
            "view_settings": {
                "exclude_quotes": True,
                "exclude_bibliography": True,
                "exclude_citations": False,
                "exclude_abstract": False,
                "exclude_methods": False,
                "exclude_custom_sections": False,
                "exclude_preprints": False,
                "exclude_small_matches": 8,
                "exclude_internet": False,
                "exclude_publications": False,
                "exclude_crossref": False,
                "exclude_crossref_posted_content": False,
                "exclude_submitted_works": False,
            },
        }
        current_user_id = self.get_user_data()["user_id"]
        current_user = User.objects.get(id=current_user_id)
        try:
            last_submission = TurnitinSubmission.objects.filter(
                user=current_user
            ).latest("created_at")
        except TurnitinSubmission.DoesNotExist:
            return {"success": False}
        # last_submission = 'de6784c5-471f-4220-aff1-16b6b44dffcf'
        response = put_generate_similarity_report(
            last_submission.turnitin_submission_id, payload
        )
        return response.json()

    @XBlock.json_handler
    def get_similarity_report_status(self, data, suffix=""):
        """
        Retrieves the status of the similarity report for the user's latest Turnitin submission.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: Information related to the status of the similarity report.
        """
        current_user_id = self.get_user_data()["user_id"]
        current_user = User.objects.get(id=current_user_id)
        try:
            last_submission = TurnitinSubmission.objects.filter(
                user=current_user
            ).latest("created_at")
        except TurnitinSubmission.DoesNotExist:
            return {"success": False}
        # last_submission = 'de6784c5-471f-4220-aff1-16b6b44dffcf'
        response = get_similarity_report_info(last_submission.turnitin_submission_id)
        return response.json()

    @XBlock.json_handler
    def create_similarity_viewer(self, data, suffix=""):
        """
        Creates a Turnitin similarity viewer for the user's latest submission.

        Args:
            data (dict): Input data for the request.
            suffix (str, optional): Additional suffix for the request. Defaults to ''.

        Returns:
            dict: Contains the URL for the similarity viewer.
        """
        user_data = self.get_user_data()
        user_name = user_data["user_name"]
        payload = {
            "viewer_user_id": user_data["user_id"],
            "locale": "en-EN",
            "viewer_default_permission_set": "INSTRUCTOR",
            "viewer_permissions": {
                "may_view_submission_full_source": False,
                "may_view_match_submission_info": False,
                "may_view_document_details_panel": False,
            },
            "similarity": {
                "default_mode": "match_overview",
                "modes": {"match_overview": True, "all_sources": True},
                "view_settings": {"save_changes": True},
            },
            "author_metadata_override": {
                "family_name": " ".join(user_name[1:])
                if len(user_name) > 1
                else "no_last_name",
                "given_name": user_name[0] if user_name else "no_name",
            },
            "sidebar": {"default_mode": "similarity"},
        }
        current_user = User.objects.get(id=user_data["user_id"])
        try:
            last_submission = TurnitinSubmission.objects.filter(
                user=current_user
            ).latest("created_at")
        except TurnitinSubmission.DoesNotExist:
            return {"success": False}
        # last_submission = 'de6784c5-471f-4220-aff1-16b6b44dffcf'
        response = post_create_viewer_launch_url(
            last_submission.turnitin_submission_id, payload
        )
        return response.json()

    # ----------------------------------------------------------------------------

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "TurnitinXBlock",
                """<turnitin/>
             """,
            ),
            (
                "Multiple TurnitinXBlock",
                """<vertical_demo>
                <turnitin/>
                <turnitin/>
                <turnitin/>
                </vertical_demo>
             """,
            ),
        ]

    @staticmethod
    def _get_statici18n_js_url():
        """
        Returns the Javascript translation file for the currently selected language, if any.
        Defaults to English if available.
        """
        locale_code = translation.get_language()
        if locale_code is None:
            return None
        text_js = "public/js/translations/{locale_code}/text.js"
        lang_code = locale_code.split("-")[0]
        for code in (locale_code, lang_code, "en"):
            loader = ResourceLoader(__name__)
            if pkg_resources.resource_exists(
                loader.module_name, text_js.format(locale_code=code)
            ):
                return text_js.format(locale_code=code)
        return None

    @staticmethod
    def get_dummy():
        """
        Dummy method to generate initial i18n
        """
        return translation.gettext_noop("Dummy")
