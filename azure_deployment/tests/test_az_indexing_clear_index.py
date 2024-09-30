# python -m unittest tests.test_az_indexing_clear_index
from data_indexing.modules.clear_index import clear_index

import unittest
from unittest.mock import MagicMock, patch


class TestClearIndex(unittest.TestCase):

    def setUp(self):
        self.search_client = MagicMock()
        self.batch_size = 2

    @patch("time.sleep", return_value=None)  # To avoid pauses in tests
    def test_clear_index_success(self, mock_sleep):
        self.search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            [],  # The second search returns an empty list, simulating that all documents have been deleted
        ]
        self.search_client.delete_documents.return_value = (
            None  # Simulate successful deletion
        )

        clear_index(self.search_client, batch_size=self.batch_size)

        self.assertEqual(self.search_client.search.call_count, 2)
        self.assertEqual(self.search_client.delete_documents.call_count, 2)
        self.search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        self.search_client.delete_documents.assert_any_call(documents=[{"id": "3"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_empty(self, mock_sleep):
        self.search_client.search.return_value = []

        clear_index(self.search_client, batch_size=self.batch_size)

        self.assertEqual(self.search_client.search.call_count, 1)
        self.assertEqual(self.search_client.delete_documents.call_count, 0)

    @patch("time.sleep", return_value=None)
    def test_clear_index_with_error(self, mock_sleep):
        self.search_client.search.return_value = [{"id": "1"}, {"id": "2"}]
        self.search_client.delete_documents.side_effect = Exception("Random error")

        clear_index(self.search_client, batch_size=self.batch_size)

        self.assertEqual(self.search_client.search.call_count, 1)
        self.assertEqual(self.search_client.delete_documents.call_count, 1)

    @patch("time.sleep", return_value=None)
    def test_clear_index_multiple_batches(self, mock_sleep):
        self.search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}],
            [],  # The second search returns an empty list
        ]
        self.search_client.delete_documents.return_value = None

        clear_index(self.search_client, batch_size=self.batch_size)

        self.assertEqual(self.search_client.search.call_count, 2)
        self.assertEqual(self.search_client.delete_documents.call_count, 3)
        self.search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        self.search_client.delete_documents.assert_any_call(
            documents=[{"id": "3"}, {"id": "4"}]
        )
        self.search_client.delete_documents.assert_any_call(documents=[{"id": "5"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_partial_failure(self, mock_sleep):
        self.search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            [],
        ]
        self.search_client.delete_documents.side_effect = [
            None,  # First deletion successful
            Exception("Random error"),  # Second deletion fails
        ]

        with patch(
            "builtins.print"
        ) as mocked_print:  # Patch print to check for error message
            clear_index(self.search_client, batch_size=self.batch_size)
            mocked_print.assert_any_call(
                "An error occurred while clearing the index: Random error"
            )

        self.assertEqual(self.search_client.search.call_count, 1)
        self.assertEqual(self.search_client.delete_documents.call_count, 2)
        self.search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        self.search_client.delete_documents.assert_any_call(documents=[{"id": "3"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_exact_batch_size(self, mock_sleep):
        self.search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}],
            [],  # The second search returns an empty list
        ]
        self.search_client.delete_documents.return_value = None

        clear_index(self.search_client, batch_size=self.batch_size)

        self.assertEqual(self.search_client.search.call_count, 2)
        self.assertEqual(self.search_client.delete_documents.call_count, 1)
        self.search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )


if __name__ == "__main__":
    unittest.main()
