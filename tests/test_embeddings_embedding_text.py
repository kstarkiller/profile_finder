#python -m unittest tests.test_embeddings_embedding_text

import unittest
from unittest.mock import patch, MagicMock
import os
from embedding_data.embeddings import embedding_text

class TestEmbeddingText(unittest.TestCase):

    # Cas de test de succès
    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_embedding_text_success(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            text = "Test text"
            model = "test-model"
            result = embedding_text(text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key='fake_api_key',
                api_version="2024-02-01",
                azure_endpoint='https://fake.endpoint'
            )
            mock_client.embeddings.create.assert_called_once_with(input=[text], model=model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_special_characters(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            special_text = "Hello, world! 😃🚀✨"
            model = "test-model"
            result = embedding_text(special_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key='fake_api_key',
                api_version="2024-02-01",
                azure_endpoint='https://fake.endpoint'
            )
            mock_client.embeddings.create.assert_called_once_with(input=[special_text], model=model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_long_text(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            long_text = "A" * 10000
            model = "test-model"
            result = embedding_text(long_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key='fake_api_key',
                api_version="2024-02-01",
                azure_endpoint='https://fake.endpoint'
            )
            mock_client.embeddings.create.assert_called_once_with(input=[long_text], model=model)

    # Cas de test d'erreurs
    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_missing_api_key(self, MockAzureOpenAI):
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': '',
            'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'
        }):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_invalid_model(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception('Model not found')
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'fake_api_key',
            'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'
        }):
            text = "Test text"
            model = "invalid-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_missing_endpoint(self, MockAzureOpenAI):
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'fake_api_key',
            'AZURE_OPENAI_ENDPOINT': ''
        }):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)
                
    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_missing_text(self, MockAzureOpenAI):
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            text = ""  
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_network_error(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception('Network error')
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch('embedding_data.embeddings.AzureOpenAI')
    def test_invalid_text_type(self, MockAzureOpenAI):
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': 'fake_api_key', 'AZURE_OPENAI_ENDPOINT': 'https://fake.endpoint'}):
            invalid_text = 12345
            model = "test-model"
            with self.assertRaises(TypeError):
                embedding_text(invalid_text, model)

if __name__ == '__main__':
    unittest.main()

