import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

# Patchez les appels au niveau du module
with patch('faiss.read_index') as mock_read_index, \
     patch('pandas.read_csv') as mock_read_csv:
    
    mock_read_csv.return_value = pd.DataFrame({
        'Combined': ["Profile 0", "Profile 1", "Profile 2"]
    })
    mock_read_index.return_value = MagicMock()

    from local_search import find_profiles  # Importez la fonction après avoir patché

class TestFindProfiles(unittest.TestCase):

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_success(self, mock_normalize_text, mock_embedding_text):
        # Simulez les retours des fonctions mockées
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.return_value = np.array([0.1, 0.2, 0.3]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[0.1, 0.2, 0.3]]), np.array([[0, 1, 2]]))

        # Appel de la fonction à tester
        user_input = "example input"
        profiles = find_profiles(user_input)

        # Assertions
        expected_profiles = ["Profile 0", "Profile 1", "Profile 2"]
        self.assertEqual(profiles, expected_profiles)

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_no_results(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.return_value = np.array([0.1, 0.2, 0.3]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[0.1, 0.2, 0.3]]), np.array([[]]))

        user_input = "example input"
        profiles = find_profiles(user_input)

        self.assertEqual(profiles, [])

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_exception_during_normalization(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.side_effect = Exception("Normalization error")

        user_input = "example input"
        profiles = find_profiles(user_input)

        self.assertEqual(profiles, [])

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_exception_during_embedding(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.side_effect = Exception("Embedding error")

        user_input = "example input"
        profiles = find_profiles(user_input)

        self.assertEqual(profiles, [])

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_index_out_of_bounds(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.return_value = np.array([0.1, 0.2, 0.3]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[0.1, 0.2, 0.3]]), np.array([[0, 10, 20]]))

        user_input = "example input"
        profiles = find_profiles(user_input)

        self.assertEqual(profiles, ["Profile 0"])

    # Nouveaux tests

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_empty_input(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = ""
        mock_embedding_text.return_value = np.array([]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[]]), np.array([[]]))

        user_input = ""
        profiles = find_profiles(user_input)

        self.assertEqual(profiles, [])

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_partial_results(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.return_value = np.array([0.1, 0.2, 0.3]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))

        user_input = "example input"
        profiles = find_profiles(user_input)

        expected_profiles = ["Profile 0", "Profile 1"]
        self.assertEqual(profiles, expected_profiles)

    @patch('embedding_data.embeddings.embedding_text')
    @patch('processing_data.normalizing.normalize_text')
    def test_find_profiles_with_duplicate_results(self, mock_normalize_text, mock_embedding_text):
        mock_normalize_text.return_value = "normalized input"
        mock_embedding_text.return_value = np.array([0.1, 0.2, 0.3]).astype("float32").reshape(1, -1)
        mock_read_index.return_value.search.return_value = (np.array([[0.1, 0.1]]), np.array([[0, 0]]))

        user_input = "example input"
        profiles = find_profiles(user_input)

        expected_profiles = ["Profile 0", "Profile 0"]
        self.assertEqual(profiles, expected_profiles)

if __name__ == '__main__':
    unittest.main()
