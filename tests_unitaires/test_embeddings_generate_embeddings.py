# python -m unittest tests.test_embeddings_generate_embeddings
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from data_embedding.modules.generate_embedded_column import generate_embeddings


class TestGenerateEmbeddings(unittest.TestCase):
    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings(self, mock_embedding_text):
        # Create a DataFrame
        data = {
            "text": ["This is a test", "Another test", "Last test"],
        }
        df = pd.DataFrame(data)
        embedding_column = "embedding"
        embedded_column = "text"
        model = "test-model"
        mock_embedding_text.side_effect = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = generate_embeddings(df, embedding_column, embedded_column, model)
        expected_result = {
            "text": ["This is a test", "Another test", "Last test"],
            "embedding": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        }
        expected_result_df = pd.DataFrame(expected_result)
        pd.testing.assert_frame_equal(result, expected_result_df)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_non_string_values(self, mock_embedding_text):
        # Create a DataFrame
        data = {
            "text": ["This is a test", 123, "Last test"],
        }
        df = pd.DataFrame(data)
        embedding_column = "embedding"
        embedded_column = "text"
        model = "test-model"
        mock_embedding_text.side_effect = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = generate_embeddings(df, embedding_column, embedded_column, model)
        expected_result = {
            "text": ["This is a test", 123, "Last test"],
            "embedding": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        }
        expected_result_df = pd.DataFrame(expected_result)
        pd.testing.assert_frame_equal(result, expected_result_df)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_embedded_column(self, mock_embedding_text):
        # Create a DataFrame
        data = {
            "text": ["This is a test", "Another test", "Last test"],
            "embedded": [None, None, None],
        }
        df = pd.DataFrame(data)
        embedding_column = "text"
        embedded_column = "no_embedded"
        model = "test-model"
        with self.assertRaises(KeyError):
            generate_embeddings(df, embedding_column, embedded_column, model)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_model(self, mock_embedding_text):
        # Create a DataFrame
        data = {
            "text": ["This is a test", "Another test", "Last test"],
            "embedded": [None, None, None],
        }
        df = pd.DataFrame(data)
        embedding_column = "text"
        embedded_column = "embedded"
        model = ""
        with self.assertRaises(ValueError):
            generate_embeddings(df, embedding_column, embedded_column, model)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_dataframe(self, mock_embedding_text):
        embedding_column = "text"
        embedded_column = "embedded"
        model = "test-model"
        with self.assertRaises(ValueError):
            generate_embeddings(None, embedding_column, embedded_column, model)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_embedding_column(self, mock_embedding_text):
        # Create a DataFrame
        data = {
            "text": ["This is a test", "Another test", "Last test"],
            "embedded": [None, None, None],
        }
        df = pd.DataFrame(data)
        embedding_column = "text"
        embedded_column = "embedded"
        model = "test-model"
        with self.assertRaises(ValueError):
            generate_embeddings(df, "", embedded_column, model)


if __name__ == "__main__":
    unittest.main()
