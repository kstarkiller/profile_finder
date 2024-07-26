#python -m unittest tests.test_normalizing_normalize_text
import unittest
from processing_data.normalizing import normalize_text  # Remplacez 'your_module' par le nom de votre module

class TestNormalizeText(unittest.TestCase):

    def test_normalize_text_with_multiple_spaces_and_special_characters(self):
        input_text = "Hello,    world! This   is a    test."
        expected_output = "Hello, world! This is a test."
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_text_with_underscores(self):
        input_text = "Hello_world!_This_is_a_test."
        expected_output = "Hello world! This is a test."
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_text_with_newlines_and_tabs(self):
        input_text = "Hello,\nworld!\tThis is\ra\ntest."
        expected_output = "Hello, world! This is a test."
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_empty_text(self):
        input_text = ""
        expected_output = ""
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_text_with_spaces_in_start_and_end(self):
        input_text = "   Hello, world!   "
        expected_output = "Hello, world!"
        self.assertEqual(normalize_text(input_text), expected_output)

    def test_normalize_text_without_special_characters_and_multiple_spaces(self):
        input_text = "Hello, world! This is a test."
        expected_output = "Hello, world! This is a test."
        self.assertEqual(normalize_text(input_text), expected_output)

if __name__ == '__main__':
    unittest.main()
