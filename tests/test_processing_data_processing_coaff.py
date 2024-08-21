import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from io import StringIO
import os
from processing_data.processing import data_processing_coaff  # Remplacez 'processing_data.processing' par le chemin correct de votre module

class TestDataProcessingCoaff(unittest.TestCase):

    def setUp(self):
        # Créer un DataFrame de test avec des dates valides et toutes les colonnes nécessaires
        self.test_data = StringIO("""
Date Demarrage,Date de fin,Competences,Tx occup, Nom, Localisation, Missions en cours
2021-01-01,2021-03-01,Python,0.8,Project A,Location A,DISPO ICE
2021-02-01,2021-02-28,SQL,0.6,Project B,Location B,EN MISSION
""")
        self.df_test = pd.read_csv(self.test_data)

        # Sauvegarder le DataFrame de test dans un fichier temporaire
        self.test_file_path = 'test_data.csv'
        self.df_test.to_csv(self.test_file_path, index=False)

    def tearDown(self):
        # Supprimer le fichier temporaire après les tests
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch('os.path.exists')
    @patch('tiktoken.get_encoding')
    def test_file_exists(self, mock_get_encoding, mock_exists):
        # Configuration des mocks
        mock_exists.return_value = True
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda text: text.split()
        mock_get_encoding.return_value = mock_tokenizer

        try:
            data_processing_coaff(self.test_file_path, 'mock_tokenizer')
        except FileNotFoundError:
            self.fail("data_processing_coaff a levé FileNotFoundError alors que le fichier existe")

    @patch('os.path.exists')
    def test_file_not_found(self, mock_exists):
        # Configuration du mock
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            data_processing_coaff('non_existent_file.csv', 'mock_tokenizer')

    @patch('os.path.exists')  # Mock de la fonction 'os.path.exists' pour contrôler son comportement pendant le test
    @patch('tiktoken.get_encoding')  # Mock de la fonction 'tiktoken.get_encoding' pour simuler le tokenizer
    def test_create_month_column(self, mock_get_encoding, mock_exists):

        mock_exists.return_value = True  # Simule l'existence du fichier pour éviter une erreur de fichier non trouvé
        mock_tokenizer = MagicMock()  # Crée un objet MagicMock pour le tokenizer
        mock_tokenizer.encode.side_effect = lambda text: text.split()  # Simule l'encodage du texte en le découpant en mots
        mock_get_encoding.return_value = mock_tokenizer  # Associe le tokenizer simulé au retour de la fonction 'get_encoding'

        # Appelle la fonction 'data_processing_coaff' avec le chemin du fichier de test et le tokenizer mocké
        df, _ = data_processing_coaff(self.test_file_path, 'mock_tokenizer')
        
        # Vérifie que la colonne 'Mois' a été correctement créée dans le DataFrame résultant
        expected_months = ["January 2021, February 2021, March 2021", "February 2021"]  # Valeurs attendues dans la colonne 'Mois'
        self.assertListEqual(df["Mois"].tolist(), expected_months)  # Compare la liste des mois générés avec les valeurs attendues


    @patch('os.path.exists')
    @patch('tiktoken.get_encoding')
    def test_column_competences(self, mock_get_encoding, mock_exists):
        # Configuration des mocks
        mock_exists.return_value = True
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda text: text.split()
        mock_get_encoding.return_value = mock_tokenizer

        df, _ = data_processing_coaff(self.test_file_path, 'mock_tokenizer')

        # Vérifier que la colonne 'Competences' contient les valeurs attendues
        expected_competences = ["Python", "SQL"]
        self.assertListEqual(df["Competences"].tolist(), expected_competences)

    @patch('os.path.exists')
    @patch('tiktoken.get_encoding')
    def test_correct_number_of_rows(self, mock_get_encoding, mock_exists):
        # Configuration des mocks
        mock_exists.return_value = True
        mock_tokenizer = MagicMock()
        mock_tokenizer.encode.side_effect = lambda text: text.split()
        mock_get_encoding.return_value = mock_tokenizer

        df, _ = data_processing_coaff(self.test_file_path, 'mock_tokenizer')

        # Vérifier que le nombre de lignes dans le DataFrame final est correct
        self.assertEqual(len(df), 2)  # Devrait être égal au nombre de lignes initiales

if __name__ == '__main__':
    unittest.main()
