# Command : python -m unittest test_unitaires.test_perplexity
import unittest
from unittest.mock import patch, MagicMock
import logging
import requests

from llm_module.generate_response import generate_perplexity_response


# The goal of this test is to verify that the generate_perplexity_response function works as expected.
class TestGeneratePerplexityResponse(unittest.TestCase):
    def setUp(self):
        # Mock the requests.post to return a mock response object
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        # patch(
        #     "llm_module.generate_response.requests.post",
        #     return_value=self.mock_response,
        # ).start()

        # Deactivate logging
        logging.disable(logging.CRITICAL)

        # Define test history
        self.test_history = [
            {
                "role": "system",
                "content": "test",
            },
            {
                "role": "user",
                "content": "test_question",
            },
        ]

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_generate_perplexity_response_success(self):
        response = generate_perplexity_response(
            ["test_data"], self.test_history, "llama-3.1-70b-instruct"
        )
        self.assertEqual(response, "test_answer")

    def test_generate_perplexity_response_no_data(self):
        response = generate_perplexity_response(
            [""], self.test_history, "llama-3.1-70b-instruct"
        )
        self.assertEqual(
            response,
            "Sorry, no data was provided. I need data to respond to your question. Please provide the data and try again.",
        )

    def test_generate_perplexity_response_no_question(self):
        test_history_no_question = [
            {
                "role": "system",
                "content": "test",
            },
            {
                "role": "user",
                "content": "",
            },
        ]
        response = generate_perplexity_response(
            ["test_data"], test_history_no_question, "llama-3.1-70b-instruct"
        )
        self.assertEqual(
            response,
            "I don't have a question to respond to. Please provide a valid question.",
        )

    def test_generate_perplexity_response_question_too_long(self):
        test_history_too_long = [
            {
                "role": "system",
                "content": "test",
            },
            {
                "role": "user",
                "content": "a" * 513,
            },
        ]
        response = generate_perplexity_response(
            ["test_data"], test_history_too_long, "llama-3.1-70b-instruct"
        )
        self.assertEqual(
            response,
            "The question is too long. Please provide a question with less than 512 characters.",
        )


if __name__ == "__main__":
    unittest.main()
