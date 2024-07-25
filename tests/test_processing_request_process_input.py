import unittest
from unittest.mock import MagicMock, patch
from processing_request import process_input

class TestProcessInput(unittest.TestCase):

    def setUp(self):
        # Set up the mocks for the dependencies
        patcher_find_profiles_azure = patch('processing_request.find_profiles_azure')
        patcher_client = patch('processing_request.client')
        patcher_EMBEDDER = patch('processing_request.EMBEDDER')
        patcher_LLM = patch('processing_request.LLM')

        self.mock_find_profiles_azure = patcher_find_profiles_azure.start()
        self.mock_client = patcher_client.start()
        self.mock_EMBEDDER = patcher_EMBEDDER.start()
        self.mock_LLM = patcher_LLM.start()
        
        self.addCleanup(patcher_find_profiles_azure.stop)
        self.addCleanup(patcher_client.stop)
        self.addCleanup(patcher_EMBEDDER.stop)
        self.addCleanup(patcher_LLM.stop)

        # Mock data
        self.mock_find_profiles_azure.return_value = ["Profile 1", "Profile 2"]
        self.mock_completion = MagicMock()
        self.mock_completion.choices = [MagicMock(message=MagicMock(content="Mock response"))]
        self.mock_client.chat.completions.create.return_value = self.mock_completion

    def test_process_input_success(self):
        user_input = [{"query": "example query"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.mock_find_profiles_azure.assert_called_once_with("example query", self.mock_EMBEDDER)
        self.mock_client.chat.completions.create.assert_called_once()

        self.assertEqual(response, "Mock response")
        self.assertEqual(len(updated_chat_history), 3)
        self.assertEqual(updated_chat_history[-1]["content"], "Mock response")

    def test_process_input_invalid_input(self):
        user_input = [{"query": "  "}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "Please enter a valid input.")
        self.assertEqual(len(updated_chat_history), 0)

    def test_process_input_no_choices(self):
        self.mock_completion.choices = []
        self.mock_client.chat.completions.create.return_value = self.mock_completion

        user_input = [{"query": "example query"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "An error occurred while processing the input.")
        self.assertEqual(len(updated_chat_history), 2)

    def test_process_input_exception(self):
        self.mock_client.chat.completions.create.side_effect = Exception("Completion error")

        user_input = [{"query": "example query"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "An error occurred while processing the input.")
        self.assertEqual(len(updated_chat_history), 2)

    def test_process_input_multiple_context(self):
        user_input = [{"context": "context 1", "query": "query 1"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.mock_find_profiles_azure.assert_called_once_with("context 1, query 1", self.mock_EMBEDDER)
        self.mock_client.chat.completions.create.assert_called_once()

        self.assertEqual(response, "Mock response")
        self.assertEqual(len(updated_chat_history), 3)
        self.assertEqual(updated_chat_history[-1]["content"], "Mock response")

    # Tests supplémentaires

    def test_process_input_empty_input(self):
        user_input = [{"query": ""}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "Please enter a valid input.")
        self.assertEqual(len(updated_chat_history), 0)

    def test_process_input_single_character_input(self):
        user_input = [{"query": "a"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.mock_find_profiles_azure.assert_called_once_with("a", self.mock_EMBEDDER)
        self.mock_client.chat.completions.create.assert_called_once()

        self.assertEqual(response, "Mock response")
        self.assertEqual(len(updated_chat_history), 3)
        self.assertEqual(updated_chat_history[-1]["content"], "Mock response")

    def test_process_input_long_text_input(self):
        long_text = "a" * 10000
        user_input = [{"query": long_text}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.mock_find_profiles_azure.assert_called_once_with(long_text, self.mock_EMBEDDER)
        self.mock_client.chat.completions.create.assert_called_once()

        self.assertEqual(response, "Mock response")
        self.assertEqual(len(updated_chat_history), 3)
        self.assertEqual(updated_chat_history[-1]["content"], "Mock response")

    def test_process_input_special_characters(self):
        special_text = "Hello, world! 😃🚀✨"
        user_input = [{"query": special_text}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.mock_find_profiles_azure.assert_called_once_with(special_text, self.mock_EMBEDDER)
        self.mock_client.chat.completions.create.assert_called_once()

        self.assertEqual(response, "Mock response")
        self.assertEqual(len(updated_chat_history), 3)
        self.assertEqual(updated_chat_history[-1]["content"], "Mock response")

    def test_process_input_client_side_error(self):
        self.mock_client.chat.completions.create.side_effect = Exception("400 Bad Request")

        user_input = [{"query": "example query"}]
        chat_history = [{"role": "system", "content": "Initial context"}]

        response, updated_chat_history = process_input(user_input, chat_history)

        self.assertEqual(response, "An error occurred while processing the input.")
        self.assertEqual(len(updated_chat_history), 2)

if __name__ == '__main__':
    unittest.main()
