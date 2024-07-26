# python -m unittest tests.test_processing_tokenizing

import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from processing_data.processing import tokenizing  # Remplacez 'your_module' par le nom de votre module

class TestTokenizing(unittest.TestCase):

    @patch('tiktoken.get_encoding')
    def test_tokenizing_success(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        data = {
            "Nom": ["Alice", "Bob"],
            "Localisation": ["Paris", "Lyon"],
            "Competences": ["Python", "Data Analysis"],
            "Missions en cours": ["DISPO ICE", "Projet X"],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", "2024-06-30"],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, 0.5],
        }
        df = pd.DataFrame(data)

        result_df, total_tokens = tokenizing(df)

        self.assertIn("combined", result_df.columns)
        self.assertIn("n_tokens", result_df.columns)
        self.assertEqual(result_df["n_tokens"].iloc[0], 20)
        self.assertEqual(result_df["n_tokens"].iloc[1], 23)
        self.assertEqual(total_tokens, 43)

    @patch('tiktoken.get_encoding')
    def test_tokenizing_empty_dataframe(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        df = pd.DataFrame(columns=["Nom", "Localisation", "Competences", "Missions en cours", "Date Demarrage", "Date de fin", "Mois", "Taux occupation"])

        result_df, total_tokens = tokenizing(df)

        self.assertEqual(len(result_df), 0)
        self.assertEqual(total_tokens, 0)

    @patch('tiktoken.get_encoding')
    def test_tokenizing_with_missing_values(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        data = {
            "Nom": ["Alice", "Bob"],
            "Localisation": ["Paris", None],
            "Competences": [None, "Data Analysis"],
            "Missions en cours": ["DISPO ICE", None],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", None],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, None],
        }
        df = pd.DataFrame(data)

        # Remplacer les valeurs NaN par des valeurs par défaut appropriées
        df["Localisation"] = df["Localisation"].fillna("Unknown")
        df["Competences"] = df["Competences"].fillna("None")
        df["Missions en cours"] = df["Missions en cours"].fillna("None")
        df["Date de fin"] = df["Date de fin"].fillna("Unknown")
        df["Taux occupation"] = df["Taux occupation"].fillna(0)

        result_df, total_tokens = tokenizing(df)

        self.assertIn("combined", result_df.columns)
        self.assertIn("n_tokens", result_df.columns)
        self.assertTrue(result_df["n_tokens"].iloc[0] > 0)
        self.assertTrue(result_df["n_tokens"].iloc[1] > 0)
        self.assertTrue(total_tokens > 0)

    @patch('tiktoken.get_encoding')
    def test_tokenizing_with_special_characters(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        data = {
            "Nom": ["Alice!", "Bob@"],
            "Localisation": ["Paris#", "Lyon$"],
            "Competences": ["Python%", "Data Analysis^"],
            "Missions en cours": ["DISPO ICE", "Projet X"],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", "2024-06-30"],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, 0.5],
        }
        df = pd.DataFrame(data)

        result_df, total_tokens = tokenizing(df)

        self.assertIn("combined", result_df.columns)
        self.assertIn("n_tokens", result_df.columns)
        self.assertTrue(result_df["n_tokens"].iloc[0] > 0)
        self.assertTrue(result_df["n_tokens"].iloc[1] > 0)
        self.assertTrue(total_tokens > 0)

    @patch('tiktoken.get_encoding')
    def test_tokenizing_with_extra_columns(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        data = {
            "Nom": ["Alice", "Bob"],
            "Localisation": ["Paris", "Lyon"],
            "Competences": ["Python", "Data Analysis"],
            "Missions en cours": ["DISPO ICE", "Projet X"],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", "2024-06-30"],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, 0.5],
            "Extra Column": ["Extra1", "Extra2"],  # Colonne supplémentaire
        }
        df = pd.DataFrame(data)

        result_df, total_tokens = tokenizing(df)

        self.assertIn("combined", result_df.columns)
        self.assertIn("n_tokens", result_df.columns)
        self.assertTrue(result_df["n_tokens"].iloc[0] > 0)
        self.assertTrue(result_df["n_tokens"].iloc[1] > 0)
        self.assertTrue(total_tokens > 0)
        # On ne vérifie pas que la colonne supplémentaire est absente,
        # mais on vérifie que les colonnes attendues sont présentes

    @patch('tiktoken.get_encoding')
    def test_tokenizing_with_incorrect_data_types(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        # Data with incorrect data types
        data = {
            "Nom": ["Alice", ["Bob"]],
            "Localisation": ["Paris", "Lyon"],
            "Competences": ["Python", "Data Analysis"],
            "Missions en cours": ["DISPO ICE", "Projet X"],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", "2024-06-30"],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, 0.5],
        }
        df = pd.DataFrame(data)

        result_df, total_tokens = tokenizing(df)

        # Vérifier que le DataFrame résultant contient les colonnes attendues
        self.assertIn("combined", result_df.columns)
        self.assertIn("n_tokens", result_df.columns)

        # Vérifier que le nombre total de tokens est calculé
        self.assertTrue(total_tokens > 0)

    @patch('tiktoken.get_encoding')
    def test_tokenizing_with_missing_required_columns(self, mock_get_encoding):
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda x: x.split()
        mock_get_encoding.return_value = mock_tokenizer

        # Données avec des colonnes requises manquantes
        data = {
            "Nom": ["Alice", "Bob"],
            "Localisation": ["Paris", "Lyon"],
            # "Competences": ["Python", "Data Analysis"],  # Colonne requise manquante
            "Missions en cours": ["DISPO ICE", "Projet X"],
            "Date Demarrage": ["2024-01-01", "2024-02-01"],
            "Date de fin": ["2024-12-31", "2024-06-30"],
            "Mois": ["Janvier", "Février"],
            "Taux occupation": [0.8, 0.5],
        }
        df = pd.DataFrame(data)

        with self.assertRaises(KeyError):
            result_df, total_tokens = tokenizing(df)


if __name__ == '__main__':
    unittest.main()


