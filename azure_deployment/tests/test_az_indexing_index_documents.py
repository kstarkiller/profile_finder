import unittest
from unittest.mock import MagicMock, patch
from azure.core.exceptions import HttpResponseError
from data_indexing.modules.index_documents import index_documents


class TestIndexDocuments(unittest.TestCase):

    def setUp(self):
        self.search_client = MagicMock()
        self.documents = [{"id": 1}, {"id": 2}, {"id": 3}]
        self.batch_size = 2

    @patch("time.sleep", return_value=None)  # To avoid pauses in tests
    def test_index_documents_success(self, mock_sleep):
        self.search_client.upload_documents.return_value = [1, 2, 3]

        index_documents(self.search_client, self.documents, batch_size=self.batch_size)

        self.assertEqual(self.search_client.upload_documents.call_count, 2)
        self.search_client.upload_documents.assert_any_call(
            documents=[{"id": 1}, {"id": 2}]
        )
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 3}])

    @patch("time.sleep", return_value=None)
    def test_index_documents_batch_too_large(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [
            HttpResponseError(
                message="Request Entity Too Large", response=MagicMock(status_code=413)
            ),
            [1, 2],  # Second attempt succeeded with reduced batch
            [3, 4],  # Third attempt succeeded with reduced batch
        ]

        documents = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
        index_documents(self.search_client, documents, batch_size=4)

        self.assertEqual(self.search_client.upload_documents.call_count, 3)
        self.search_client.upload_documents.assert_any_call(
            documents=[{"id": 1}, {"id": 2}]
        )
        self.search_client.upload_documents.assert_any_call(
            documents=[{"id": 3}, {"id": 4}]
        )

    @patch("time.sleep", return_value=None)
    def test_index_documents_general_error(self, mock_sleep):
        self.search_client.upload_documents.side_effect = Exception("Random error")

        with self.assertRaises(Exception) as context:
            index_documents(
                self.search_client, self.documents, batch_size=self.batch_size
            )

        self.assertEqual(
            str(context.exception), "Failed to index batch after 3 retries"
        )
        self.assertEqual(self.search_client.upload_documents.call_count, 3)

    @patch("time.sleep", return_value=None)
    def test_index_documents_empty_batch(self, mock_sleep):
        documents = []
        index_documents(self.search_client, documents, batch_size=self.batch_size)

        self.assertEqual(self.search_client.upload_documents.call_count, 0)

    @patch("time.sleep", return_value=None)
    def test_index_documents_invalid_documents(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [
            Exception("Invalid document")
        ]

        with self.assertRaises(Exception) as context:
            index_documents(
                self.search_client, self.documents, batch_size=self.batch_size
            )

        self.assertEqual(
            str(context.exception), "Failed to index batch after 3 retries"
        )
        self.assertEqual(self.search_client.upload_documents.call_count, 3)

    @patch("time.sleep", return_value=None)
    def test_index_documents_small_batch(self, mock_sleep):
        self.search_client.upload_documents.return_value = [1]

        documents = [{"id": 1}]
        index_documents(self.search_client, documents, batch_size=1)

        self.assertEqual(self.search_client.upload_documents.call_count, 1)
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 1}])

    @patch("time.sleep", return_value=None)  # To avoid pauses in tests
    def test_index_documents_one_retry(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [Exception("Temporary error")]

        with self.assertRaises(Exception) as context:
            index_documents(
                self.search_client,
                self.documents,
                batch_size=self.batch_size,
                max_retries=1,
            )

        self.assertEqual(
            str(context.exception), "Failed to index batch after 1 retries"
        )
        self.assertEqual(self.search_client.upload_documents.call_count, 1)

    @patch("time.sleep", return_value=None)  # To avoid pauses in tests
    def test_index_documents_mixed_exceptions(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [
            HttpResponseError(
                message="Request Entity Too Large", response=MagicMock(status_code=413)
            ),
            Exception("Random error"),
            HttpResponseError(
                message="Request Entity Too Large", response=MagicMock(status_code=413)
            ),
        ]

        with self.assertRaises(Exception) as context:
            index_documents(self.search_client, self.documents, batch_size=4)

        self.assertEqual(
            str(context.exception), "Failed to index batch after 3 retries"
        )
        self.assertEqual(self.search_client.upload_documents.call_count, 3)

    @patch("time.sleep", return_value=None)
    def test_index_documents_duplicate_ids(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [[1, 2, 3], [4, 5]]

        documents = [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 3}, {"id": 4}, {"id": 5}]
        index_documents(self.search_client, documents, batch_size=3)

        self.assertEqual(self.search_client.upload_documents.call_count, 2)
        self.search_client.upload_documents.assert_any_call(
            documents=[{"id": 1}, {"id": 2}, {"id": 1}]
        )
        self.search_client.upload_documents.assert_any_call(
            documents=[{"id": 3}, {"id": 4}, {"id": 5}]
        )

    @patch("time.sleep", return_value=None)
    def test_index_documents_batch_size_one(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [[1], [2], [3]]

        index_documents(self.search_client, self.documents, batch_size=1)

        self.assertEqual(self.search_client.upload_documents.call_count, 3)
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 1}])
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 2}])
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 3}])

    @patch("time.sleep", return_value=None)
    def test_index_documents_empty_response(self, mock_sleep):
        self.search_client.upload_documents.side_effect = [[], [], []]

        index_documents(self.search_client, self.documents, batch_size=1)

        self.assertEqual(self.search_client.upload_documents.call_count, 3)
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 1}])
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 2}])
        self.search_client.upload_documents.assert_any_call(documents=[{"id": 3}])


if __name__ == "__main__":
    unittest.main()
