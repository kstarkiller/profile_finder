# python -m unittest tests.test_az_embeddings_embedding_text
import unittest
from unittest.mock import patch, MagicMock
import os
from data_embedding.modules.embed_text import embedding_text


class TestEmbeddingText(unittest.TestCase):

    # Define a test function that mocks the AzureOpenAI class from the embed_text module
    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_embedding_text_success(self, MockAzureOpenAI):
        # Create an instance of the mocked AzureOpenAI class
        mock_client = MockAzureOpenAI.return_value

        # Define the return value of the embeddings.create method of the mocked client
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])  # Mocked embedding data to return
        ]

        # Temporarily set environment variables for the API key and Azure OpenAI endpoint
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            # Define the input text and model to use in the embedding_text function
            text = "Test text"
            model = "test-model"

            # Call the embedding_text function with the test text and model
            result = embedding_text(text, model)

            # Verify that the result matches the expected embedding values
            self.assertEqual(result, [0.1, 0.2, 0.3])

            # Verify that the AzureOpenAI class was instantiated with the correct parameters
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",  # Ensure the correct API version is used
                azure_endpoint="https://fake.endpoint",
            )

            # Verify that the embeddings.create method was called once with the correct inputs and model
            mock_client.embeddings.create.assert_called_once_with(
                input=[text], model=model
            )

    # Notes:
    # - @patch is used to replace the AzureOpenAI class with a mock during the test.
    # - MockAzureOpenAI.return_value provides a mocked instance of the AzureOpenAI class.
    # - patch.dict is used to temporarily set environment variables in the test.
    # - MagicMock is used to create a mocked return value for the embedding data.
    # - self.assertEqual and self.assert_called_once_with are used to verify the expected test results.

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_special_characters(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            special_text = "Hello, world! 😃🚀✨"
            model = "test-model"
            result = embedding_text(special_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",
                azure_endpoint="https://fake.endpoint",
            )
            mock_client.embeddings.create.assert_called_once_with(
                input=[special_text], model=model
            )

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_long_text(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            long_text = "A" * 10000
            model = "test-model"
            result = embedding_text(long_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",
                azure_endpoint="https://fake.endpoint",
            )
            mock_client.embeddings.create.assert_called_once_with(
                input=[long_text], model=model
            )

    # Error test cases
    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_api_key(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_invalid_model(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception("Model not found")
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "invalid-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_endpoint(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_API_KEY": "fake_api_key", "AZURE_OPENAI_ENDPOINT": ""},
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_text(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = ""
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_network_error(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception("Network error")
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_invalid_text_type(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            invalid_text = 12345
            model = "test-model"
            with self.assertRaises(TypeError):
                embedding_text(invalid_text, model)


if __name__ == "__main__":
    unittest.main()
