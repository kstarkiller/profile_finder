# python -m unittest tests.test_az_indexing_index_documents
import unittest
from unittest.mock import MagicMock, patch
from azure.core.exceptions import HttpResponseError
from data_indexing.modules.index_documents import index_documents

class TestIndexDocuments(unittest.TestCase):

    @patch('time.sleep', return_value=None)  # Pour éviter les pauses dans les tests
    def test_index_documents_success(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.return_value = [1, 2, 3]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        index_documents(search_client, documents, batch_size=2)

        self.assertEqual(search_client.upload_documents.call_count, 2)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}, {"id": 2}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 3}])

    @patch('time.sleep', return_value=None)
    def test_index_documents_batch_too_large(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [
            HttpResponseError(message="Request Entity Too Large", response=MagicMock(status_code=413)),
            [1, 2],  # Seconde tentative réussie avec batch réduit
            [3, 4]   # Troisième tentative réussie avec batch réduit
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        index_documents(search_client, documents, batch_size=4)

        self.assertEqual(search_client.upload_documents.call_count, 3)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}, {"id": 2}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 3}, {"id": 4}])

    @patch('time.sleep', return_value=None)
    def test_index_documents_general_error(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = Exception("Random error")

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        with self.assertRaises(Exception) as context:
            index_documents(search_client, documents, batch_size=2)

        self.assertEqual(str(context.exception), "Failed to index batch after 3 retries")
        self.assertEqual(search_client.upload_documents.call_count, 3)

    @patch('time.sleep', return_value=None)
    def test_index_documents_empty_batch(self, mock_sleep):
        search_client = MagicMock()

        documents = []
        index_documents(search_client, documents, batch_size=2)

        self.assertEqual(search_client.upload_documents.call_count, 0)

    @patch('time.sleep', return_value=None)
    def test_index_documents_invalid_documents(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [Exception("Invalid document")]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        with self.assertRaises(Exception) as context:
            index_documents(search_client, documents, batch_size=2)

        self.assertEqual(str(context.exception), "Failed to index batch after 3 retries")
        self.assertEqual(search_client.upload_documents.call_count, 3)

    @patch('time.sleep', return_value=None)
    def test_index_documents_small_batch(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.return_value = [1]

        documents = [{"id": 1}]
        index_documents(search_client, documents, batch_size=1)

        self.assertEqual(search_client.upload_documents.call_count, 1)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}])


    @patch('time.sleep', return_value=None)  # Pour éviter les pauses dans les tests
    def test_index_documents_one_retry(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [Exception("Temporary error")]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        with self.assertRaises(Exception) as context:
            index_documents(search_client, documents, batch_size=2, max_retries=1)

        self.assertEqual(str(context.exception), "Failed to index batch after 1 retries")
        self.assertEqual(search_client.upload_documents.call_count, 1)


    @patch('time.sleep', return_value=None)  # Pour éviter les pauses dans les tests
    def test_index_documents_mixed_exceptions(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [
            HttpResponseError(message="Request Entity Too Large", response=MagicMock(status_code=413)),
            Exception("Random error"),
            HttpResponseError(message="Request Entity Too Large", response=MagicMock(status_code=413)),
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        with self.assertRaises(Exception) as context:
            index_documents(search_client, documents, batch_size=4)

        self.assertEqual(str(context.exception), "Failed to index batch after 3 retries")
        self.assertEqual(search_client.upload_documents.call_count, 3)


    # Nouveau test : gestion des documents avec des ID en double
    @patch('time.sleep', return_value=None)
    def test_index_documents_duplicate_ids(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [
            [1, 2, 3],
            [4, 5]
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}, {"id": 4}, {"id": 5}]
        index_documents(search_client, documents, batch_size=3)

        self.assertEqual(search_client.upload_documents.call_count, 2)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}, {"id": 2}, {"id": 1}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 3}, {"id": 4}, {"id": 5}])

    # Nouveau test : gestion de l'indexation avec une taille de batch de 1
    @patch('time.sleep', return_value=None)
    def test_index_documents_batch_size_one(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [
            [1],
            [2],
            [3]
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        index_documents(search_client, documents, batch_size=1)

        self.assertEqual(search_client.upload_documents.call_count, 3)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 2}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 3}])

    # Nouveau test : gestion d'une réponse vide de l'API
    @patch('time.sleep', return_value=None)
    def test_index_documents_empty_response(self, mock_sleep):
        search_client = MagicMock()
        search_client.upload_documents.side_effect = [
            [],
            [],
            []
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        index_documents(search_client, documents, batch_size=1)

        self.assertEqual(search_client.upload_documents.call_count, 3)
        search_client.upload_documents.assert_any_call(documents=[{"id": 1}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 2}])
        search_client.upload_documents.assert_any_call(documents=[{"id": 3}])

if __name__ == '__main__':
    unittest.main()
