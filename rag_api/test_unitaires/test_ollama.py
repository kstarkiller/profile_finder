# Command: python -m unittest test_unitaires.test_ollama
import unittest
from unittest.mock import patch, MagicMock
import logging

from llm_module.generate_response import generate_ollama_response


# The goal of this test is to verify that the generate_ollama_response function works as expected.
class TestGenerateOllamaResponse(unittest.TestCase):
    def setUp(self):
        # Mock the ollama object
        self.mock_ollama = MagicMock()
        self.mock_ollama.list.return_value = {
            "models": [
                {"name": "nomic-embed-text:latest"},
                {"name": "all-minilm:33m"},
                {"name": "llama3.1:8b"},
            ]
        }
        self.mock_ollama.generate.return_value = {"response": "Test response"}
        patch("llm_module.generate_response.ollama", self.mock_ollama).start()

        # Automatically provide the username and password to avoid user input when testing
        self.patcher_input = patch(
            "llm_module.generate_response.input", return_value="test_user"
        )
        self.patcher_getpass = patch("getpass.getpass", return_value="test_pass")
        self.mock_input = self.patcher_input.start()
        self.mock_getpass = self.patcher_getpass.start()

        # Deactivate logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_generate_ollama_response_success(self):
        history = [
            {"role": "system", "content": "test_text1"},
            {"role": "user", "content": "test_text2"},
        ]
        response = generate_ollama_response([["test_data"]], history)
        self.assertEqual(response, "Test response")

    def test_generate_ollama_response_no_question(self):
        history = [
            {"role": "system", "content": "test_text1"},
            {"role": "user", "content": ""},
        ]
        response = generate_ollama_response(["test_data"], history)
        self.assertEqual(
            response,
            "I don't have a question to respond to. Please provide a valid question.",
        )

    def test_generate_ollama_response_question_too_long(self):
        history = [
            {"role": "test_role1", "content": "test_text1"},
            {"role": "test_role1", "content": "a" * 513},
        ]
        response = generate_ollama_response(["test_data"], history)
        self.assertEqual(
            response,
            "The question is too long. Please provide a question with less than 512 characters.",
        )

    def test_generate_ollama_response_invalid_model(self):
        history = [
            {"role": "system", "content": "test_text1"},
            {"role": "user", "content": "test_text2"},
        ]
        response = generate_ollama_response(["test_data"], history, "invalid_model")
        self.assertEqual(
            response,
            "The model invalid_model is not available. Please choose a valid model from this list: ['nomic-embed-text:latest', 'all-minilm:33m', 'llama3.1:8b']",
        )
