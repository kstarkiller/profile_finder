# python -m unittest tests.test_embeddings_embedding_text
import unittest
from unittest.mock import patch, MagicMock
import os
from data_embedding.modules.embed_text import embedding_text


class TestEmbeddingText(unittest.TestCase):

    # Définir une fonction de test qui mocke la classe AzureOpenAI du module embed_text
    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_embedding_text_success(self, MockAzureOpenAI):
        # Créer une instance de la classe AzureOpenAI mockée
        mock_client = MockAzureOpenAI.return_value

        # Définir la valeur de retour de la méthode embeddings.create du client mocké
        mock_client.embeddings.create.return_value.data = [
            MagicMock(
                embedding=[0.1, 0.2, 0.3]
            )  # Données d'embedding mockées à retourner
        ]

        # Définir temporairement des variables d'environnement pour la clé API et le point d'accès Azure OpenAI
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            # Définir le texte d'entrée et le modèle à utiliser dans la fonction embedding_text
            text = "Test text"
            model = "test-model"

            # Appeler la fonction embedding_text avec le texte et le modèle de test
            result = embedding_text(text, model)

            # Vérifier que le résultat correspond aux valeurs d'embedding attendues
            self.assertEqual(result, [0.1, 0.2, 0.3])

            # Vérifier que la classe AzureOpenAI a été instanciée avec les bons paramètres
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",  # Assurer que la bonne version de l'API est utilisée
                azure_endpoint="https://fake.endpoint",
            )

            # Vérifier que la méthode embeddings.create a été appelée une fois avec les bonnes entrées et le bon modèle
            mock_client.embeddings.create.assert_called_once_with(
                input=[text], model=model
            )

    # Remarques :
    # - @patch est utilisé pour remplacer la classe AzureOpenAI par un mock pendant le test.
    # - MockAzureOpenAI.return_value fournit une instance mockée de la classe AzureOpenAI.
    # - patch.dict est utilisé pour définir temporairement des variables d'environnement dans le test.
    # - MagicMock est utilisé pour créer une valeur de retour mockée pour les données d'embedding.
    # - self.assertEqual et self.assert_called_once_with sont utilisés pour vérifier les résultats attendus du test.

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_special_characters(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            special_text = "Hello, world! 😃🚀✨"
            model = "test-model"
            result = embedding_text(special_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",
                azure_endpoint="https://fake.endpoint",
            )
            mock_client.embeddings.create.assert_called_once_with(
                input=[special_text], model=model
            )

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_long_text(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3])
        ]
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            long_text = "A" * 10000
            model = "test-model"
            result = embedding_text(long_text, model)
            self.assertEqual(result, [0.1, 0.2, 0.3])
            MockAzureOpenAI.assert_called_once_with(
                api_key="fake_api_key",
                api_version="2024-02-01",
                azure_endpoint="https://fake.endpoint",
            )
            mock_client.embeddings.create.assert_called_once_with(
                input=[long_text], model=model
            )

    # Cas de test d'erreurs
    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_api_key(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_invalid_model(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception("Model not found")
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "invalid-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_endpoint(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {"AZURE_OPENAI_API_KEY": "fake_api_key", "AZURE_OPENAI_ENDPOINT": ""},
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_missing_text(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = ""
            model = "test-model"
            with self.assertRaises(ValueError):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_network_error(self, MockAzureOpenAI):
        mock_client = MockAzureOpenAI.return_value
        mock_client.embeddings.create.side_effect = Exception("Network error")
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            text = "Test text"
            model = "test-model"
            with self.assertRaises(Exception):
                embedding_text(text, model)

    @patch("data_embedding.modules.embed_text.AzureOpenAI")
    def test_invalid_text_type(self, MockAzureOpenAI):
        with patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_API_KEY": "fake_api_key",
                "AZURE_OPENAI_ENDPOINT": "https://fake.endpoint",
            },
        ):
            invalid_text = 12345
            model = "test-model"
            with self.assertRaises(TypeError):
                embedding_text(invalid_text, model)


if __name__ == "__main__":
    unittest.main()
