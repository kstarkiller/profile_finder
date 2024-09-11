# Command : python -m unittest test_unitaires.test_generate_response
# The goal of this test is to verify that the generate_response function works as expected.
import unittest
from unittest.mock import patch, MagicMock
import logging

from generate_response import generate_response as generate_response
from generate_response import authenticate as authenticate
import config as config

class TestGenerateResponse(unittest.TestCase):
    def setUp(self):
        self.mock_ollama = MagicMock()
        self.mock_ollama.list_models.return_value = ['llama3.1:8b']
        self.mock_ollama.generate.return_value = {'response': 'Test response'}

        patch('generate_response.ollama', self.mock_ollama).start()
        patch('generate_response.authenticate', return_value=True).start()

        # Deactivate logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_generate_response_success(self):
        response = generate_response('test_data', 'test_question')
        self.assertEqual(response, 'Test response')

    def test_generate_response_no_data(self):
        response = generate_response('', 'test_question')
        self.assertEqual(response, """Sorry, no data was provided. I need data to respond to your question. Please provide the data and try again.""")

    def test_generate_response_no_question(self):
        response = generate_response('test_data', '')
        self.assertEqual(response, """I don't have a question to respond to. Please provide a valid question.""")

    def test_generate_response_question_too_long(self):
        response = generate_response('test_data', 'a' * 513)
        self.assertEqual(response, """The question is too long. Please provide a question with less than 512 characters.""")

    def test_generate_response_invalid_model(self):
        response = generate_response('test_data', 'test_question', 'invalid_model')
        self.assertEqual(response, """The model invalid_model is not available. Please choose a valid model from this list: ['llama3.1:8b']""")

    def test_generate_response_access_denied(self):
        patch('generate_response.authenticate', return_value=False).start()
        response = generate_response('test_data', 'test_question')
        self.assertEqual(response, "Access denied. Invalid credentials.")

    def test_generate_response_no_authenticate(self):
        with patch('generate_response.authenticate', return_value=False):
            response = generate_response('test_data', 'test_question')
            self.assertEqual(response, "Access denied. Invalid credentials.")


class TestAuthenticate(unittest.TestCase):
    def setUp(self):
        # Patch the input and getpass functions
        self.patcher_input = patch('builtins.input')
        self.patcher_getpass = patch('getpass.getpass')
        
        self.mock_input = self.patcher_input.start()
        self.mock_getpass = self.patcher_getpass.start()

        # Patch the congig values
        patch('config.USERNAME', 'test_username').start()
        patch('config.PASSWORD', 'test_password').start()

        # Deactivate logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_authenticate_success(self):
        self.mock_input.return_value = 'test_username'
        self.mock_getpass.return_value = 'test_password'
        self.assertTrue(authenticate())

    def test_authenticate_failure(self):
        self.mock_input.return_value = 'test_username'
        self.mock_getpass.return_value = 'wrong_password'
        self.assertFalse(authenticate())

    def test_authenticate_no_username(self):
        self.mock_input.side_effect = ['', 'test_username']
        self.mock_getpass.return_value = 'test_password'
        self.assertFalse(authenticate())

    def test_authenticate_no_password(self):
        self.mock_input.return_value = 'test_username'
        self.mock_getpass.return_value = ''
        self.assertFalse(authenticate())

    def test_authenticate_no_credentials(self):
        self.mock_input.side_effect = ['', '']
        self.mock_getpass.return_value = ''
        self.assertFalse(authenticate())

if __name__ == '__main__':
    unittest.main()