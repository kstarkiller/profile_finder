# Command: python -m unittest test_unitaires.test_rag_api
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from rag_api import app  # Assurez-vous d'importer votre application FastAPI


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("rag_api.mlflow")
    def test_root(self, mock_mlflow):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "API is running"})

    @patch("rag_api.mlflow")
    def test_test_endpoint(self, mock_mlflow):
        response = self.client.post("/test", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello Success"})

    @patch("rag_api.store_file")
    @patch("rag_api.download_files")
    @patch("rag_api.get_skills")
    @patch("rag_api.create_fixtures")
    @patch("rag_api.insert_profiles")
    @patch("rag_api.delete_collection")
    @patch("rag_api.embed_documents")
    @patch("rag_api.run_validation", return_value=(MagicMock(), 0))
    @patch("rag_api.mlflow")
    @patch(
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
    def test_storing_file(
        self,
        mock_docker,
        mock_mlflow,
        mock_validation,
        mock_embed,
        mock_delete,
        mock_insert,
        mock_create,
        mock_get_skills,
        mock_download,
        mock_store,
    ):
        mock_store.return_value = "Successfully stored"
        mock_download.return_value = "Files downloaded"
        mock_get_skills.return_value = []
        mock_create.return_value = "Fixtures created"
        mock_insert.return_value = "Profiles inserted"
        mock_delete.return_value = "Collection deleted"
        mock_embed.return_value = "Documents embedded"
        mock_validation.return_value = (MagicMock(), 0)

        with open("test_file.txt", "w") as f:
            f.write("test")

        with open("test_file.txt", "rb") as file:
            response = self.client.post(
                "/file", files={"file": ("test_file.txt", file)}
            )

        self.assertEqual(response.status_code, 200)

    @patch("rag_api.download_files")
    @patch(
        "rag_api.is_running_in_docker",
        return_value={
            "mongo_user": "user",
            "mongo_pwd": "pwd",
            "mongo_host": "host",
            "mongo_port": "port",
            "mongo_db": "db",
        },
    )
    def test_getting_file(self, mock_docker, mock_download):
        mock_download.return_value = "mock file content"
        response = self.client.get("/file")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "mock file content"})

    @patch("rag_api.requests.delete")
    @patch("rag_api.requests.get")
    @patch(
        "rag_api.is_running_in_docker",
        return_value={"db_api_host": "api_host", "db_api_port": "port"},
    )
    def test_storing_profiles(self, mock_docker, mock_get, mock_delete):
        mock_get.return_value.json.return_value = {"profiles": []}  # No profiles in db
        mock_get.return_value.status_code = 200
        mock_delete.return_value.status_code = 200

        response = self.client.get("/profiles")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    @patch("rag_api.requests.delete")
    @patch("rag_api.requests.get")
    @patch(
        "rag_api.is_running_in_docker",
        return_value={"db_api_host": "api_host", "db_api_port": "port"},
    )
    def test_truncate_table(self, mock_docker, mock_get, mock_delete):
        mock_delete.return_value.status_code = 200
        mock_delete.return_value.json.return_value = {}

        response = self.client.delete("/profiles")
        self.assertEqual(response.status_code, 200)

    @patch("rag_api.embed_documents")
    @patch(
        "rag_api.is_running_in_docker", return_value={"collection": "mock_collection"}
    )
    def test_embedding(self, mock_docker, mock_embed):
        mock_embed.return_value = "Embedding complete"
        response = self.client.post("/embed")
        self.assertEqual(response.status_code, 200)
        self.assertIn("collection", response.json())

    @patch("rag_api.retrieve_documents")
    @patch("rag_api.generate_ollama_response")
    @patch("rag_api.generate_minai_response")
    @patch("rag_api.mlflow")
    @patch(
        "rag_api.is_running_in_docker",
        return_value={"db_api_host": "api_host", "db_api_port": "port"},
    )
    def test_process_question(
        self,
        mock_docker,
        mock_mlflow,
        mock_generate_minai,
        mock_generate_ollama,
        mock_retrieve,
    ):
        mock_retrieve.return_value = "mock data"
        mock_generate_ollama.return_value = "mock response"
        input_data = {
            "service_type": "ollama",
            "question": "What is AI?",
            "history": [],
            "chat_id": "123",
            "model": "gpt-4o-mini",
        }

        response = self.client.get("/chat", params=input_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())

    @patch("rag_api.generate_conversation_id")
    def test_new_chat_id(self, mock_generate_id):
        mock_generate_id.return_value = "new_chat_123"
        input_data = {"model": "gpt-4o-mini", "prompt": "Tell me about AI"}
        response = self.client.get(
            "/chat/id", params=input_data
        )  # Changez à params au lieu de json
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"new_id": "new_chat_123"})


if __name__ == "__main__":
    unittest.main()
