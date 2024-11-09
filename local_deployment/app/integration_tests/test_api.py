# python -m unittest discover -s integration_tests
import unittest
import requests
import os

base_path = os.path.dirname(__file__)


class TestRAGAPIIntegration(unittest.TestCase):
    BASE_URL = "http://localhost:8080"
    TOKEN_URL = f"{BASE_URL}/token"
    USERNAME = "test"

    def get_token(self):
        response = requests.get(self.TOKEN_URL, params={"username": self.USERNAME})
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def test_root_endpoint(self):
        response = requests.get(f"{self.BASE_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("API is running", response.json()["message"])

    def test_chat(self):
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "service_type": "minai",
            "question": "Hello",
            "history": {"role": "user", "content": "Hello"},
            "chat_id": "chat_id123",
            "model": "gpt-4o-mini",
        }

        response = requests.post(f"{self.BASE_URL}/chat", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["response"], str)


class TestBDDAPIIntegration(unittest.TestCase):
    BASE_URL = "http://localhost:5050"

    def test_get_profiles(self):
        response = requests.get(f"{self.BASE_URL}/profiles", json={"type": "perm"})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["profiles"], list)

    def test_delete_user(self):
        payload = {"email": "test2@example.com", "password": "password"}
        response = requests.delete(f"{self.BASE_URL}/user", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("User deleted", response.json())

    def test_create_user(self):
        payload = {
            "name": "Test User",
            "email": "test2@example.com",
            "password": "password",
        }
        response = requests.put(f"{self.BASE_URL}/user", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)


if __name__ == "__main__":
    unittest.main()
