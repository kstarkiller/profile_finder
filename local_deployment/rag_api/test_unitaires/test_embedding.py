# Command: python -m unittest test_unitaires.test_embedding
import unittest
from unittest.mock import patch, MagicMock
from chromadb.config import Settings

from rag_module.embedding import embed_documents


class TestEmbedDocuments(unittest.TestCase):

    def setUp(self):
        # Patch the methods and start the patches
        self.patcher_load_profile = patch("rag_module.embedding.load_profile")
        self.patcher_PersistentClient = patch("chromadb.PersistentClient")
        self.patcher_ollama_embeddings = patch("ollama.embeddings")

        # Start the patches
        self.mock_load_profile = self.patcher_load_profile.start()
        self.mock_PersistentClient = self.patcher_PersistentClient.start()
        self.mock_ollama_embeddings = self.patcher_ollama_embeddings.start()

        # Configure the mock PersistentClient
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_PersistentClient.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def tearDown(self):
        # Stop all patches
        patch.stopall()

    def test_embed_documents_success(self):
        # Test-specific setup
        self.mock_load_profile.return_value = ["Document 1", "Document 2"]
        self.mock_ollama_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        # Call the function with batch_size=1
        collection = embed_documents("dummy_path", "temp", batch_size=1)

        # Assertions
        self.mock_PersistentClient.assert_called_once_with(
            path="dummy_path", settings=Settings(allow_reset=True)
        )
        self.mock_client.get_or_create_collection.assert_called_once_with(name="temp")
        self.mock_load_profile.assert_called_once_with("temp")
        self.assertEqual(self.mock_collection.add.call_count, 2)

    def test_embed_documents_load_profile_error(self):
        # Test-specific setup
        self.mock_load_profile.side_effect = ValueError("Error loading documents")

        # Call the function and check the exception
        with self.assertRaises(ValueError):
            embed_documents(
                "dummy_path", "temp",
            )

    def test_embed_documents_invalid_documents_type(self):
        # Test-specific setup
        self.mock_load_profile.return_value = "Invalid type"

        # Call the function and check the exception
        with self.assertRaises(ValueError):
            embed_documents(
                "dummy_path", "temp",
            )

    def test_embed_documents_ollama_error(self):
        # Test-specific setup
        self.mock_load_profile.return_value = ["Document 1"]
        self.mock_ollama_embeddings.side_effect = ValueError("Ollama error")

        # Call the function and check the exception
        with self.assertRaises(ValueError):
            embed_documents(
                "dummy_path", "temp",
            )


if __name__ == "__main__":
    unittest.main()
