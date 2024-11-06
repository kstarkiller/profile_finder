# Command: python -m unittest test_unitaires.test_load_documents
import unittest
from unittest.mock import patch, MagicMock
import requests

from rag_module.load_documents import load_profile as load_profile
from docker_check import is_running_in_docker

venv = is_running_in_docker()


class TestLoadProfile(unittest.TestCase):

    def setUp(self):
        self.url = f"http://{venv['db_api_host']}:{venv['db_api_port']}/get_profiles"

    def mock_response(self, status_code=200, json_data=None, raise_for_status=None):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {}
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        return mock_resp

    @patch("requests.get")
    def test_load_profile_success(self, mock_get):
        mock_get.return_value = self.mock_response(
            json_data={
                "profiles": [{"combined": "Profile 1"}, {"combined": "Profile 2"}]
            }
        )

        result = load_profile()
        expected_result = ["Profile 1", "Profile 2"]
        self.assertEqual(result, expected_result)

    @patch("requests.get")
    def test_load_profile_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError("API Error")

        with self.assertRaises(ValueError) as context:
            load_profile()

        self.assertEqual(str(context.exception), "Error loading profiles: API Error")

    @patch("requests.get")
    def test_load_profile_no_profiles(self, mock_get):
        mock_get.return_value = self.mock_response(json_data={"profiles": []})

        result = load_profile()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
