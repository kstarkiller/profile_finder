# Command: python -m unittest test_unitaires.test_authenticate
import unittest
from unittest.mock import patch
import logging

from llm_module.generate_response import authenticate


# The goal of this test is to verify that the authenticate function works as expected.
class TestAuthenticate(unittest.TestCase):
    def setUp(self):
        # Patch the config values
        self.patcher1 = patch("llm_module.generate_response.USERNAME", "test_username")
        self.patcher2 = patch("llm_module.generate_response.PASSWORD", "test_password")
        self.patcher3 = patch(
            "builtins.input", side_effect=["test_username", "test_password"]
        )

        self.mock_username = self.patcher1.start()
        self.mock_password = self.patcher2.start()
        self.mock_input = self.patcher3.start()

        # Deactivate logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_authenticate_success(self):
        self.assertTrue(authenticate("test_username", "test_password"))

    def test_authenticate_failure(self):
        self.assertFalse(authenticate("test_username", "wrong_password"))

    def test_authenticate_no_username(self):
        self.assertFalse(authenticate("", "test_password"))

    def test_authenticate_no_password(self):
        self.assertFalse(authenticate("test_username", ""))

    def test_authenticate_no_credentials(self):
        self.assertFalse(authenticate("", ""))


if __name__ == "__main__":
    unittest.main()
