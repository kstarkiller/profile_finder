# Command : python -m unittest test_unitaires.test_load_documents
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from load_documents import load_documents as load_documents
import config as config

# The goal of this test is to verify that the load_documents function works as expected.
class TestLoadDocuments(unittest.TestCase):

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pandas.read_csv')
    def test_load_documents_success(self, mock_read_csv, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ['test.csv']
        mock_read_csv.return_value = pd.DataFrame({'Combined': ['line1\nline2']})
        
        result = load_documents("dummy_path")
        
        self.assertEqual(result, ['line1', 'line2'])

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_load_documents_no_csv(self, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ['test.txt']
        
        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    @patch('os.path.exists')
    def test_load_documents_directory_not_exist(self, mock_exists):
        # Setup mocks
        mock_exists.return_value = False
        
        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pandas.read_csv')
    def test_load_documents_error_reading_file(self, mock_read_csv, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ['test.csv']
        mock_read_csv.side_effect = ValueError("Erreur de lecture")
        
        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pandas.read_csv')
    def test_load_documents_no_file_in_directory(self, mock_read_csv, mock_listdir, mock_exists):
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = []
        
        with self.assertRaises(ValueError):
            load_documents("dummy_path")

# Run the tests
if __name__ == '__main__':
    unittest.main()


