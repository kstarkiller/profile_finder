#python -m unittest tests.test_embeddings_generate_embeddings
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from data_embedding.modules.generate_embedded_column import generate_embeddings

class TestGenerateEmbeddings(unittest.TestCase):

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_success(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3]
        data = {'Combined': ['text1', 'text2', 'text3']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': ['text1', 'text2', 'text3'], 'embedding': [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_empty_dataframe(self, mock_embedding_text):
        df = pd.DataFrame({'Combined': []})
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_df = pd.DataFrame({'Combined': [], 'embedding': []})
        pd.testing.assert_frame_equal(result_df, expected_df)
        self.assertEqual(len(mock_embedding_text.mock_calls), 0)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_numeric_and_date(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3]
        data = {'Combined': [123, '2023-07-17', 'Sample text']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': [123, '2023-07-17', 'Sample text'], 'embedding': [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_special_characters(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3]
        data = {'Combined': ['text!@#$', 'another%^&*', 'more()_+']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': ['text!@#$', 'another%^&*', 'more()_+'], 'embedding': [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_null_values(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3] if text else None
        data = {'Combined': ['text1', None, 'text3']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': ['text1', None, 'text3'], 'embedding': [[0.1, 0.2, 0.3], None, [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_nan_values(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3] if not pd.isnull(text) else None
        data = {'Combined': ['text1', float('nan'), 'text3']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': ['text1', float('nan'), 'text3'], 'embedding': [[0.1, 0.2, 0.3], None, [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_long_texts(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3]
        long_text = 'a' * 10000  # Très long texte
        data = {'Combined': [long_text, 'short text']}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        expected_data = {'Combined': [long_text, 'short text'], 'embedding': [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]}
        expected_df = pd.DataFrame(expected_data)
        pd.testing.assert_frame_equal(result_df, expected_df)

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_invalid_column(self, mock_embedding_text):
        data = {'InvalidColumn': ['text1', 'text2', 'text3']}
        df = pd.DataFrame(data)
        with self.assertRaises(KeyError):
            generate_embeddings(df, 'embedding', 'Combined', 'test-model')

    # @patch('indexing_data.embeddings.embedding_text')
    # def test_generate_embeddings_with_non_textual_values(self, mock_embedding_text):
    #     data = {'Combined': [{'key': 'value'}, ['list', 'of', 'items'], set(['a', 'set'])]}
    #     df = pd.DataFrame(data)
    #     with self.assertRaises(TypeError):
    #         generate_embeddings(df, 'embedding', 'Combined', 'test-model')

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_missing_column(self, mock_embedding_text):
        data = {'OtherColumn': ['text1', 'text2', 'text3']}
        df = pd.DataFrame(data)
        with self.assertRaises(KeyError):
            generate_embeddings(df, 'embedding', 'Combined', 'test-model')

    @patch('indexing_data.embeddings.embedding_text')
    def test_generate_embeddings_with_multiple_columns(self, mock_embedding_text):
        mock_embedding_text.side_effect = lambda text, model: [0.1, 0.2, 0.3]
        data = {'Combined': ['text1', 'text2', 'text3'], 'OtherColumn': [1, 2, 3]}
        df = pd.DataFrame(data)
        result_df = generate_embeddings(df, 'embedding', 'Combined', 'test-model')
        
        # Vérifier que les colonnes Combined et embedding sont présentes
        self.assertIn('Combined', result_df.columns)
        self.assertIn('embedding', result_df.columns)
        
        # Vérifier les valeurs des colonnes Combined et embedding
        expected_data = {
            'Combined': ['text1', 'text2', 'text3'],
            'embedding': [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]
        }
        expected_df = pd.DataFrame(expected_data)
        
        pd.testing.assert_frame_equal(result_df, expected_df[['Combined', 'embedding']])



if __name__ == '__main__':
    unittest.main()

