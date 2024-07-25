# python -m unittest tests.test_az_search_find_profile_azure
import unittest
from unittest.mock import MagicMock, patch
from az_search import find_profiles_azure

class TestFindProfilesAzure(unittest.TestCase):

    def setUp(self):
        # Set up mocks for each test
        self.mock_normalize_text = MagicMock(return_value="normalized input")
        self.mock_embedding_text = MagicMock(return_value=[0.1, 0.2, 0.3])
        self.mock_VectorizedQuery = MagicMock(return_value="vectorized query")
        self.mock_search_client = MagicMock()

        # Patch the external dependencies in the target module
        self.patcher_normalize_text = patch('az_search.normalize_text', self.mock_normalize_text)
        self.patcher_embedding_text = patch('az_search.embedding_text', self.mock_embedding_text)
        self.patcher_VectorizedQuery = patch('az_search.VectorizedQuery', self.mock_VectorizedQuery)
        self.patcher_search_client = patch('az_search.search_client', self.mock_search_client)

        # Start patching
        self.patcher_normalize_text.start()
        self.patcher_embedding_text.start()
        self.patcher_VectorizedQuery.start()
        self.patcher_search_client.start()

    def tearDown(self):
        # Stop patching
        self.patcher_normalize_text.stop()
        self.patcher_embedding_text.stop()
        self.patcher_VectorizedQuery.stop()
        self.patcher_search_client.stop()

    def test_find_profiles_azure_success(self):
        # Mock search results
        self.mock_search_client.search.return_value = [
            {"content": "Profile 1"},
            {"content": "Profile 2"}
        ]

        # Call the function to test
        user_input = "example input"
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.mock_normalize_text.assert_called_once_with(user_input)
        self.mock_embedding_text.assert_called_once_with("normalized input", model)
        self.mock_VectorizedQuery.assert_called_once_with(
            vector=[0.1, 0.2, 0.3],
            k_nearest_neighbors=10,
            fields="content_vector",
            kind="vector"
        )
        self.mock_search_client.search.assert_called_once_with(
            search_text=None,
            vector_queries=["vectorized query"],
            select=["id", "content"],
            top=10
        )
        self.assertEqual(profiles, ["Profile 1", "Profile 2"])

    def test_find_profiles_azure_no_results(self):
        # Mock search results
        self.mock_search_client.search.return_value = []

        # Call the function to test
        user_input = "example input"
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.assertEqual(profiles, [])

    def test_find_profiles_azure_exception(self):
        # Mock an exception during normalization
        self.mock_normalize_text.side_effect = Exception("Normalization error")

        # Call the function to test
        user_input = "example input"
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.assertEqual(profiles, [])

    def test_find_profiles_azure_single_result(self):
        # Mock search results
        self.mock_search_client.search.return_value = [
            {"content": "Profile 1"}
        ]

        # Call the function to test
        user_input = "example input"
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.assertEqual(profiles, ["Profile 1"])

    def test_find_profiles_azure_empty_input(self):
        # Call the function to test with empty input
        user_input = ""
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.mock_normalize_text.assert_called_once_with(user_input)
        self.mock_embedding_text.assert_called_once_with("normalized input", model)
        self.mock_VectorizedQuery.assert_called_once_with(
            vector=[0.1, 0.2, 0.3],
            k_nearest_neighbors=10,
            fields="content_vector",
            kind="vector"
        )
        self.mock_search_client.search.assert_called_once_with(
            search_text=None,
            vector_queries=["vectorized query"],
            select=["id", "content"],
            top=10
        )

    def test_find_profiles_azure_long_input(self):
        # Call the function to test with a long input
        user_input = "a" * 10000
        model = "example model"
        profiles = find_profiles_azure(user_input, model)

        # Assertions
        self.mock_normalize_text.assert_called_once_with(user_input)
        self.mock_embedding_text.assert_called_once_with("normalized input", model)
        self.mock_VectorizedQuery.assert_called_once_with(
            vector=[0.1, 0.2, 0.3],
            k_nearest_neighbors=10,
            fields="content_vector",
            kind="vector"
        )
        self.mock_search_client.search.assert_called_once_with(
            search_text=None,
            vector_queries=["vectorized query"],
            select=["id", "content"],
            top=10
        )

if __name__ == '__main__':
    unittest.main()
