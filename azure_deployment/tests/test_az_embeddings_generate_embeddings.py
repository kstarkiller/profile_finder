# python -m unittest tests.test_az_embeddings_generate_embeddings
import unittest
from unittest.mock import patch
import pandas as pd
from data_embedding.modules.generate_embedded_column import generate_embeddings


class TestGenerateEmbeddings(unittest.TestCase):
    def setUp(self):
        self.data = {
            "text": ["This is a test", "Another test", "Last test"],
        }
        self.df = pd.DataFrame(self.data)
        self.embedding_column = "embedding"
        self.embedded_column = "text"
        self.model = "test-model"

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings(self, mock_embedding_text):
        mock_embedding_text.side_effect = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = generate_embeddings(
            self.df, self.embedding_column, self.embedded_column, self.model
        )
        expected_result = {
            "text": ["This is a test", "Another test", "Last test"],
            "embedding": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        }
        expected_result_df = pd.DataFrame(expected_result)
        pd.testing.assert_frame_equal(result, expected_result_df)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_non_string_values(self, mock_embedding_text):
        self.df.at[1, "text"] = 123
        mock_embedding_text.side_effect = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = generate_embeddings(
            self.df, self.embedding_column, self.embedded_column, self.model
        )
        expected_result = {
            "text": ["This is a test", 123, "Last test"],
            "embedding": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        }
        expected_result_df = pd.DataFrame(expected_result)
        pd.testing.assert_frame_equal(result, expected_result_df)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_embedded_column(self, mock_embedding_text):
        self.df["embedded"] = [None, None, None]
        with self.assertRaises(KeyError):
            generate_embeddings(
                self.df, self.embedding_column, "no_embedded", self.model
            )

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_model(self, mock_embedding_text):
        self.df["embedded"] = [None, None, None]
        with self.assertRaises(ValueError):
            generate_embeddings(
                self.df, self.embedding_column, self.embedded_column, ""
            )

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_dataframe(self, mock_embedding_text):
        with self.assertRaises(ValueError):
            generate_embeddings(None, self.embedding_column, self.embedded_column, self.model)  # type: ignore

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_no_embedding_column(self, mock_embedding_text):
        self.df["embedded"] = [None, None, None]
        with self.assertRaises(ValueError):
            generate_embeddings(self.df, "", self.embedded_column, self.model)

    @patch("data_embedding.modules.generate_embedded_column.embedding_text")
    def test_generate_embeddings_with_special_characters(self, mock_embedding_text):
        self.df.at[0, "text"] = "This is a test with special characters !@#$%^&*()"
        mock_embedding_text.side_effect = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        result = generate_embeddings(
            self.df, self.embedding_column, self.embedded_column, self.model
        )
        expected_result = {
            "text": [
                "This is a test with special characters !@#$%^&*()",
                "Another test",
                "Last test",
            ],
            "embedding": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        }
        expected_result_df = pd.DataFrame(expected_result)
        pd.testing.assert_frame_equal(result, expected_result_df)


if __name__ == "__main__":
    unittest.main()
