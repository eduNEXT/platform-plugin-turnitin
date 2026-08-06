"""Tests for the platform_plugin_turnitin.utils module."""

from unittest import TestCase
from unittest.mock import Mock, patch

from requests.exceptions import RequestException

from platform_plugin_turnitin.utils import resolve_current_eula_version

UTILS_MODULE_PATH = "platform_plugin_turnitin.utils"


class TestResolveCurrentEulaVersion(TestCase):
    """Tests for the `resolve_current_eula_version` function."""

    @patch(f"{UTILS_MODULE_PATH}.get_eula_version_info")
    def test_resolves_version_from_response(self, mock_get_eula_version_info: Mock):
        """
        Test the function returns the version reported by Turnitin.

        Expected result: The version from the response body is returned.
        """
        mock_get_eula_version_info.return_value = Mock(ok=True, json=Mock(return_value={"version": "v2"}))

        result = resolve_current_eula_version()

        self.assertEqual(result, "v2")

    @patch(f"{UTILS_MODULE_PATH}.get_eula_version_info")
    def test_falls_back_on_non_ok_response(self, mock_get_eula_version_info: Mock):
        """
        Test the function falls back to "v1beta" when Turnitin returns a non-OK response.

        Expected result: The function returns "v1beta".
        """
        mock_get_eula_version_info.return_value = Mock(ok=False)

        result = resolve_current_eula_version()

        self.assertEqual(result, "v1beta")

    @patch(f"{UTILS_MODULE_PATH}.get_eula_version_info")
    def test_falls_back_on_unexpected_response_shape(self, mock_get_eula_version_info: Mock):
        """
        Test the function falls back to "v1beta" when the response body has no "version" key.

        Expected result: The function returns "v1beta".
        """
        mock_get_eula_version_info.return_value = Mock(ok=True, json=Mock(return_value={"unexpected": "shape"}))

        result = resolve_current_eula_version()

        self.assertEqual(result, "v1beta")

    @patch(f"{UTILS_MODULE_PATH}.get_eula_version_info")
    def test_falls_back_on_request_exception(self, mock_get_eula_version_info: Mock):
        """
        Test the function falls back to "v1beta" when the request itself fails.

        Expected result: The function returns "v1beta".
        """
        mock_get_eula_version_info.side_effect = RequestException

        result = resolve_current_eula_version()

        self.assertEqual(result, "v1beta")
