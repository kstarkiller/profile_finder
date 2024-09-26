# python -m unittest tests.test_az_indexing_clear_index
from data_indexing.modules.clear_index import clear_index

import unittest
from unittest.mock import MagicMock, patch


class TestClearIndex(unittest.TestCase):

    @patch("time.sleep", return_value=None)  # Pour éviter les pauses dans les tests
    def test_clear_index_success(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}, {"id": "3"}],
            [],  # La deuxième recherche renvoie une liste vide, simulant que tous les documents ont été supprimés
        ]
        search_client.delete_documents.return_value = (
            None  # Simuler la suppression réussie
        )

        clear_index(search_client, batch_size=2)

        self.assertEqual(search_client.search.call_count, 2)
        self.assertEqual(search_client.delete_documents.call_count, 2)
        search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        search_client.delete_documents.assert_any_call(documents=[{"id": "3"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_empty(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.return_value = []

        clear_index(search_client, batch_size=2)

        self.assertEqual(search_client.search.call_count, 1)
        self.assertEqual(search_client.delete_documents.call_count, 0)

    @patch("time.sleep", return_value=None)
    def test_clear_index_with_error(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.return_value = [{"id": "1"}, {"id": "2"}]
        search_client.delete_documents.side_effect = Exception("Random error")

        clear_index(search_client, batch_size=2)

        self.assertEqual(search_client.search.call_count, 1)
        self.assertEqual(search_client.delete_documents.call_count, 1)

    @patch("time.sleep", return_value=None)
    def test_clear_index_multiple_batches(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}, {"id": "3"}, {"id": "4"}, {"id": "5"}],
            [],  # La deuxième recherche renvoie une liste vide
        ]
        search_client.delete_documents.return_value = None

        clear_index(search_client, batch_size=2)

        self.assertEqual(search_client.search.call_count, 2)
        self.assertEqual(search_client.delete_documents.call_count, 3)
        search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        search_client.delete_documents.assert_any_call(
            documents=[{"id": "3"}, {"id": "4"}]
        )
        search_client.delete_documents.assert_any_call(documents=[{"id": "5"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_partial_failure(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.side_effect = [[{"id": "1"}, {"id": "2"}, {"id": "3"}], []]
        search_client.delete_documents.side_effect = [
            None,  # Première suppression réussie
            Exception("Random error"),  # Deuxième suppression échoue
        ]

        with patch(
            "builtins.print"
        ) as mocked_print:  # Patch print to check for error message
            clear_index(search_client, batch_size=2)
            mocked_print.assert_any_call(
                "An error occurred while clearing the index: Random error"
            )

        self.assertEqual(search_client.search.call_count, 1)
        self.assertEqual(search_client.delete_documents.call_count, 2)
        search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )
        search_client.delete_documents.assert_any_call(documents=[{"id": "3"}])

    @patch("time.sleep", return_value=None)
    def test_clear_index_exact_batch_size(self, mock_sleep):
        search_client = MagicMock()
        search_client.search.side_effect = [
            [{"id": "1"}, {"id": "2"}],
            [],  # La deuxième recherche renvoie une liste vide
        ]
        search_client.delete_documents.return_value = None

        clear_index(search_client, batch_size=2)

        self.assertEqual(search_client.search.call_count, 2)
        self.assertEqual(search_client.delete_documents.call_count, 1)
        search_client.delete_documents.assert_any_call(
            documents=[{"id": "1"}, {"id": "2"}]
        )


if __name__ == "__main__":
    unittest.main()
