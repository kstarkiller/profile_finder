# command: python -m unittest test_unitaires.test_rag_api
import unittest
from unittest.mock import patch, MagicMock
from requests.models import Response
import logging
from fastapi.testclient import TestClient
from rag_api import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        # Patch de is_running_in_docker
        patcher_docker = patch(
            "rag_api.is_running_in_docker",
            return_value={
                "mongo_user": "user",
                "mongo_pwd": "pwd",
                "mongo_host": "host",
                "mongo_port": "port",
                "mongo_db": "db",
                "db_api_host": "api_host",
                "db_api_port": "port",
                "mf_host": "mf_host",
                "mf_port": "mf_port",
            },
        )
        self.mock_is_running_in_docker = patcher_docker.start()
        self.addCleanup(patcher_docker.stop)

        # Factorisation des autres patches
        self.patches = []
        self.mocks = {}

        patch_targets = [
            "mlflow.end_run",
            "mlflow.start_run",
            "mlflow.set_experiment",
            "mlflow.set_tracking_uri",
            "rag_api.requests.delete",
            "rag_api.requests.get",
            "rag_api.generate_ollama_response",
            "rag_api.retrieve_documents",
            "rag_api.generate_conversation_id",
            "rag_api.delete_temp_files",
            "rag_api.process_file",
        ]

        for target in patch_targets:
            patcher = patch(target)
            mock = patcher.start()
            self.patches.append(patcher)
            self.mocks[target] = mock
            self.addCleanup(patcher.stop)

        self.client = TestClient(app)

    def tearDown(self):
        patch.stopall()
        # Activate logging
        logging.disable(logging.NOTSET)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "API is running"})

    def test_test_endpoint(self):
        response = self.client.post("/test", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello Success"})

    def test_get_token(self):
        response = self.client.get("/token", params={"username": "test"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_storing_file(self):
        mock_delete = self.mocks["rag_api.requests.delete"]
        mock_set_tracking_uri = self.mocks["mlflow.set_tracking_uri"]
        mock_set_experiment = self.mocks["mlflow.set_experiment"]
        mock_start_run = self.mocks["mlflow.start_run"]
        mock_end_run = self.mocks["mlflow.end_run"]
        mock_delete_temp_files = self.mocks["rag_api.delete_temp_files"]
        mock_process_file = self.mocks["rag_api.process_file"]

        mock_delete_temp_files.return_value = None
        mock_process_file.return_value = (MagicMock(), 0)
        mock_process_file.return_value = (MagicMock(), 0)
        mock_delete.return_value = MagicMock(
            status_code=200, json=lambda: {"message": "Profiles deleted"}
        )

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        with open("test_file.txt", "w") as f:
            f.write("test")
        with open("test_file.txt", "rb") as file:
            response = self.client.post(
                "/file",
                files={"file": ("test_file.txt", file)},
                headers={
                    "Authorization": f"Bearer {token}"
                },
            )

        self.assertEqual(response.status_code, 200)
        mock_set_tracking_uri.assert_called_once()
        mock_set_experiment.assert_called_once_with("Profile Finder RAG Metrics")
        mock_start_run.assert_called_once()
        mock_end_run.assert_called_once()

    def test_process_question_success(self):
        mock_retrieve_documents = self.mocks["rag_api.retrieve_documents"]
        mock_generate_ollama_response = self.mocks["rag_api.generate_ollama_response"]
        mock_set_tracking_uri = self.mocks["mlflow.set_tracking_uri"]
        mock_set_experiment = self.mocks["mlflow.set_experiment"]
        mock_start_run = self.mocks["mlflow.start_run"]
        mock_end_run = self.mocks["mlflow.end_run"]

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        payload = {
            "service_type": "ollama",
            "question": "What is the weather?",
            "history": [
                {"role": "system", "content": "test_content"},
                {"role": "user", "content": "What is the weather?"},
            ],
            "chat_id": "chat123",
            "model": "llama3.1:8b",
        }
        mock_retrieve_documents.return_value = (MagicMock(), 0)
        mock_generate_ollama_response.return_value = (MagicMock(), 0)

        response = self.client.post(
            "/chat",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 200)
        mock_set_tracking_uri.assert_called_once()
        mock_set_experiment.assert_called_once_with("Profile Finder Chat Metrics")
        mock_start_run.assert_called_once()
        mock_end_run.assert_called_once()

    def test_process_question_no_documents(self):
        mock_retrieve_documents = self.mocks["rag_api.retrieve_documents"]
        input_data = {
            "question": "What is the capital of France?",
            "service_type": "ollama",
            "history": [],
            "model": "default_model",
            "chat_id": "chat123",
        }

        mock_retrieve_documents.return_value = None

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        response = self.client.post(
            "/chat",
            json=input_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "500: No document found")

    def test_process_question_invalid_service_type(self):
        mock_retrieve_documents = self.mocks["rag_api.retrieve_documents"]
        input_data = {
            "question": "What is the capital of France?",
            "service_type": "invalid_service",
            "history": [],
            "model": "default_model",
            "chat_id": "chat123",
        }

        mock_retrieve_documents.return_value = ["document_data"]

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        response = self.client.post(
            "/chat",
            json=input_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "500: Incorrect service type")

    def test_process_question_exception_handling(self):
        mock_retrieve_documents = self.mocks["rag_api.retrieve_documents"]
        input_data = {
            "question": "What is the capital of France?",
            "service_type": "ollama",
            "history": [],
            "model": "default_model",
            "chat_id": "chat123",
        }

        mock_retrieve_documents.side_effect = Exception("Database error")

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        response = self.client.post(
            "/chat",
            json=input_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        self.assertEqual(response.json()["detail"], "Database error")

    def test_new_chat_id(self):
        mock_generate_id = self.mocks["rag_api.generate_conversation_id"]
        mock_generate_id.return_value = "new_chat_123"

        token_resp = self.client.get("/token", params={"username": "test"})
        token = token_resp.json()["access_token"]

        input_data = {"model": "gpt-4o-mini", "prompt": "Tell me about AI"}
        response = self.client.post(
            "/chat/id",
            json=input_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"new_id": "new_chat_123"})


if __name__ == "__main__":
    unittest.main()
