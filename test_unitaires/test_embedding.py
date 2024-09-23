# Command : python -m unittest test_unitaires.test_embedding
import unittest
from unittest.mock import patch, MagicMock
from chromadb.config import Settings

from rag_module.embedding import embed_documents
from rag_module.embedding import collection_path

class TestEmbedDocuments(unittest.TestCase):

    def setUp(self):
        # Patch les méthodes et commence les patchs
        self.patcher_load_documents = patch("rag_module.embedding.load_documents")
        self.patcher_PersistentClient = patch("chromadb.PersistentClient")
        self.patcher_ollama_embeddings = patch("ollama.embeddings")

        # Démarre les patchs
        self.mock_load_documents = self.patcher_load_documents.start()
        self.mock_PersistentClient = self.patcher_PersistentClient.start()
        self.mock_ollama_embeddings = self.patcher_ollama_embeddings.start()

        # Configure le mock PersistentClient
        self.mock_client = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_PersistentClient.return_value = self.mock_client
        self.mock_client.get_or_create_collection.return_value = self.mock_collection

    def tearDown(self):
        # Arrête tous les patchs
        patch.stopall()

    def test_embed_documents_success(self):
        # Setup spécifique au test
        self.mock_load_documents.return_value = ["Document 1", "Document 2"]
        self.mock_ollama_embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        # Appelle la fonction avec batch_size=1
        collection = embed_documents("dummy_path", batch_size=1)

        # Assertions
        self.mock_PersistentClient.assert_called_once_with(
            path=collection_path, settings=Settings(allow_reset=True)
        )
        self.mock_client.get_or_create_collection.assert_called_once_with(name="docs")
        self.mock_load_documents.assert_called_once_with("dummy_path")
        self.assertEqual(self.mock_collection.add.call_count, 2)

    def test_embed_documents_load_documents_error(self):
        # Setup spécifique au test
        self.mock_load_documents.side_effect = ValueError(
            "Erreur de chargement des documents"
        )

        # Appelle la fonction et vérifie l'exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")

    def test_embed_documents_invalid_documents_type(self):
        # Setup spécifique au test
        self.mock_load_documents.return_value = "Invalid type"

        # Appelle la fonction et vérifie l'exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")

    def test_embed_documents_ollama_error(self):
        # Setup spécifique au test
        self.mock_load_documents.return_value = ["Document 1"]
        self.mock_ollama_embeddings.side_effect = ValueError("Erreur Ollama")

        # Appelle la fonction et vérifie l'exception
        with self.assertRaises(ValueError):
            embed_documents("dummy_path")


if __name__ == "__main__":
    unittest.main()
