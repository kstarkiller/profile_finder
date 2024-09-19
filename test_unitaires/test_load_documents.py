# Command : python -m unittest test_unitaires.test_load_documents
# Command : python -m unittest test_unitaires.test_load_documents
import unittest
from unittest.mock import patch
import pandas as pd

from load_documents import load_documents as load_documents


# The goal of this test is to verify that the load_documents function works as expected.
class TestLoadDocuments(unittest.TestCase):

    def setUp(self):
        # Common setup for all tests
        self.patcher_exists = patch("os.path.exists")
        self.patcher_listdir = patch("os.listdir")
        self.patcher_read_csv = patch("pandas.read_csv")

        self.mock_exists = self.patcher_exists.start()
        self.mock_listdir = self.patcher_listdir.start()
        self.mock_read_csv = self.patcher_read_csv.start()

        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_listdir.stop)
        self.addCleanup(self.patcher_read_csv.stop)

    def tearDown(self):
        # Arrête tous les patchs
        patch.stopall()

    def test_load_documents_success(self):
        # Setup mocks specific to this test
        self.mock_exists.return_value = True
        self.mock_listdir.return_value = ["test.csv"]
        self.mock_read_csv.return_value = pd.DataFrame({"Combined": ["line1\nline2"]})

        result = load_documents("dummy_path")

        self.assertEqual(result, ["line1", "line2"])

    def test_load_documents_no_csv(self):
        # Setup mocks specific to this test
        self.mock_exists.return_value = True
        self.mock_listdir.return_value = ["test.txt"]

        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    def test_load_documents_directory_not_exist(self):
        # Setup mocks specific to this test
        self.mock_exists.return_value = False

        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    def test_load_documents_error_reading_file(self):
        # Setup mocks specific to this test
        self.mock_exists.return_value = True
        self.mock_listdir.return_value = ["test.csv"]
        self.mock_read_csv.side_effect = ValueError("Erreur de lecture")

        with self.assertRaises(ValueError):
            load_documents("dummy_path")

    def test_load_documents_no_file_in_directory(self):
        # Setup mocks specific to this test
        self.mock_exists.return_value = True
        self.mock_listdir.return_value = []

        with self.assertRaises(ValueError):
            load_documents("dummy_path")


# Run the tests
if __name__ == "__main__":
    unittest.main()
