# python -m unittest tests.test_az_processing_request_process_input
import unittest
from unittest.mock import MagicMock, patch
from llm_module.az_processing_request import process_input


class TestProcessInput(unittest.TestCase):
    @patch("llm_module.az_processing_request.find_profiles_azure")
    @patch("llm_module.az_processing_request.client.chat.completions.create")
    def test_process_input(self, mock_completion, mock_find_profiles):
        user_input = [
            {"query": "Hello, how are you?", "context": "python"},
        ]
        chat_history = [
            {"role": "system", "content": "Welcome to the chatbot!"},
        ]

        mock_find_profiles.return_value = ["profile1", "profile2"]
        mock_completion.return_value.choices = [
            MagicMock(
                message=MagicMock(
                    content="I am fine, thank you. How can I help you today?"
                )
            )
        ]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "I am fine, thank you. How can I help you today?")

        self.assertEqual(
            updated_chat_history,
            [
                {"role": "system", "content": "Welcome to the chatbot!"},
                {
                    "role": "system",
                    "content": "Use the following profiles in this conversation: profile1, profile2",
                },
                {"role": "user", "content": "Hello, how are you?"},
                {
                    "role": "assistant",
                    "content": "I am fine, thank you. How can I help you today?",
                },
            ],
        )

    def test_process_input_empty_query(self):
        user_input = [
            {"query": "", "context": "python"},
        ]
        chat_history = [
            {"role": "system", "content": "Welcome to the chatbot!"},
        ]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "Please enter a valid input.")
        self.assertEqual(updated_chat_history, chat_history)

    @patch("llm_module.az_processing_request.client.chat.completions.create")
    def test_process_input_empty_context(self, mock_completion):
        user_input = [
            {"query": "Hello, how are you?", "context": ""},
        ]
        chat_history = [
            {"role": "system", "content": "Welcome to the chatbot!"},
        ]

        mock_completion.return_value.choices = [
            MagicMock(
                message=MagicMock(
                    content="I am fine, thank you. How can I help you today?"
                )
            )
        ]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "I am fine, thank you. How can I help you today?")

        self.assertEqual(
            updated_chat_history,
            [
                {"role": "system", "content": "Welcome to the chatbot!"},
                {"role": "user", "content": "Hello, how are you?"},
                {
                    "role": "assistant",
                    "content": "I am fine, thank you. How can I help you today?",
                },
            ],
        )

    @patch("llm_module.az_processing_request.find_profiles_azure")
    @patch("llm_module.az_processing_request.client.chat.completions.create")
    def test_process_input_no_choices(self, mock_completion, mock_find_profiles):
        user_input = [
            {"query": "Hello, how are you?", "context": "python"},
        ]
        chat_history = [
            {"role": "system", "content": "Welcome to the chatbot!"},
        ]

        mock_find_profiles.return_value = ["profile1", "profile2"]
        mock_completion.return_value.choices = []

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "An error occurred while processing the input.")
        self.assertEqual(updated_chat_history, chat_history)

    @patch("llm_module.az_processing_request.find_profiles_azure")
    @patch("llm_module.az_processing_request.client.chat.completions.create")
    def test_process_input_no_content_attribute(
        self, mock_completion, mock_find_profiles
    ):
        user_input = [
            {"query": "Hello, how are you?", "context": "python"},
        ]
        chat_history = [
            {"role": "system", "content": "Welcome to the chatbot!"},
        ]

        mock_find_profiles.return_value = ["profile1", "profile2"]
        mock_completion.return_value.choices.content = []

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "An error occurred while processing the input.")
        self.assertEqual(updated_chat_history, chat_history)


if __name__ == "__main__":
    unittest.main()
