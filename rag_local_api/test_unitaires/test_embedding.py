# Command : python -m unittest test_unitaires.test_embed_documents
import os
import unittest
from unittest.mock import patch, MagicMock
import chromadb
from chromadb.config import Settings
from embedding import embed_documents
from embedding import collection_path

class TestEmbedDocuments(unittest.TestCase):

    @patch('embedding.load_documents')
    @patch('chromadb.PersistentClient')
    @patch('ollama.embeddings')
    def test_embed_documents_success(self, mock_ollama_embeddings, mock_PersistentClient, mock_load_documents):
        # Setup mocks
        mock_load_documents.return_value = ["Document 1", "Document 2"]
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ollama_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        # Call the function
        collection = embed_documents("dummy_path")

        # Assertions
        mock_PersistentClient.assert_called_once_with(
            path=collection_path,
            settings=Settings(allow_reset=True)
        )
        mock_client.get_or_create_collection.assert_called_once_with(name="docs")
        mock_load_documents.assert_called_once_with("dummy_path")
        self.assertEqual(mock_collection.add.call_count, 2)

    @patch('embedding.load_documents')
    @patch('chromadb.PersistentClient')
    def test_embed_documents_load_documents_error(self, mock_PersistentClient, mock_load_documents):
        # Setup mocks
        mock_load_documents.side_effect = ValueError("Erreur de chargement des documents")

        # Call the function and assert exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")

    @patch('embedding.load_documents')
    @patch('chromadb.PersistentClient')
    def test_embed_documents_invalid_documents_type(self, mock_PersistentClient, mock_load_documents):
        # Setup mocks
        mock_load_documents.return_value = "Invalid type"

        # Call the function and assert exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")

    @patch('embedding.load_documents')
    @patch('chromadb.PersistentClient')
    @patch('ollama.embeddings')
    def test_embed_documents_ollama_error(self, mock_ollama_embeddings, mock_PersistentClient, mock_load_documents):
        # Setup mocks
        mock_load_documents.return_value = ["Document 1"]
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_ollama_embeddings.side_effect = ValueError("Erreur Ollama")

        # Call the function and assert exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")

if __name__ == '__main__':
    unittest.main()