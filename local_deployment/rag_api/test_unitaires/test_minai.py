# Command: python -m unittest test_unitaires.test_minai
import unittest
from unittest.mock import patch, Mock
import requests

from llm_module.generate_response import generate_minai_response


class TestGenerateMinaiResponse(unittest.TestCase):

    @patch("requests.post")
    def test_valid_response(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content.decode.return_value = "Response from API"
        mock_post.return_value = mock_response

        data = ["data_example"]
        chat_id = "test_chat_id"
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        model = "test_model"

        response = generate_minai_response(data, chat_id, history, model)

        self.assertEqual(response, "Response from API")
        mock_post.assert_called_once()

    def test_empty_history(self):
        data = ["data_example"]
        chat_id = "test_chat_id"
        history = []
        model = "test_model"

        response = generate_minai_response(data, chat_id, history, model)

        self.assertEqual(response, "History is empty")

    def test_no_model_provided(self):
        data = ["data_example"]
        chat_id = "test_chat_id"
        history = [{"role": "user", "content": "Hello"}]
        model = ""

        response = generate_minai_response(data, chat_id, history, model)

        self.assertEqual(response, "No model provided")

    @patch("requests.post")
    def test_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.content.decode.return_value = (
            "I'm sorry, I can't answer you : Bad Request"
        )
        mock_post.return_value = mock_response

        data = ["data_example"]
        chat_id = "test_chat_id"
        history = [{"role": "user", "content": "Hello"}]
        model = "test_model"

        response = generate_minai_response(data, chat_id, history, model)

        self.assertEqual(response, "I'm sorry, I can't answer you : Bad Request")

    @patch("requests.post")
    def test_generic_exception(self, mock_post):
        # Simules une exception générique
        mock_post.side_effect = Exception("An error occurred")

        data = ["data_example"]
        chat_id = "test_chat_id"
        history = [{"role": "user", "content": "Hello"}]
        model = "test_model"

        response = generate_minai_response(data, chat_id, history, model)

        self.assertTrue(response.startswith("I'm sorry, I can't answer you :"))


if __name__ == "__main__":
    unittest.main()
