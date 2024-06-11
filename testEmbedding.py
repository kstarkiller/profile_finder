import pandas as pd
import requests
import json
import os
import numpy as np

# Définir le chemin du fichier CSV
csv_file_path = 'C:\\Users\\thibaut.boguszewski\\Desktop\\Tibo\\Coaff_V1.csv'

# Vérifier si le fichier existe
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"Le fichier n'a pas été trouvé : {csv_file_path}")

# Charger le fichier CSV avec un encodage approprié et le bon délimiteur
try:
    data = pd.read_csv(csv_file_path, encoding='latin1', delimiter=';')
except UnicodeDecodeError:
    print("Erreur de décodage Unicode avec l'encodage par défaut. Essayez avec un autre encodage.")
    raise
except pd.errors.ParserError as e:
    print(f"Erreur de parsing: {e}")
    raise

# Afficher les noms des colonnes pour vérifier leur contenu
print("Noms des colonnes : ", data.columns)

# Afficher les premières lignes pour vérifier le contenu
print(data.head())

# Choisir la colonne de texte à embedder (vérifiez la casse et l'orthographe)
text_column = 'Compétences'

if text_column not in data.columns:
    raise KeyError(f"La colonne '{text_column}' n'existe pas dans le fichier CSV. Vérifiez les noms des colonnes.")

# Définir le modèle et l'API URL
model_name = 'sentence-transformers/all-MiniLM-L6-v2'
api_url = f'https://api-inference.huggingface.co/models/{model_name}'

# Insérer votre token d'accès API Hugging Face
headers = {"Authorization": "Bearer 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"}

# Fonction pour nettoyer le texte avant l'envoi à l'API
def clean_text(text):
    if isinstance(text, float) and (np.isnan(text) or np.isinf(text)):
        return ""
    return str(text)

# Fonction pour obtenir les embeddings via API
def get_embeddings(text):
    cleaned_text = clean_text(text)
    response = requests.post(api_url, headers=headers, json={"inputs": cleaned_text})
    if response.status_code == 200:
        result = response.json()
        # Extraire les embeddings de la réponse
        embeddings = result[0][0] if result else []
        return embeddings
    else:
        print(f"Erreur: {response.status_code}")
        return None

# Appliquer l'embedding sur la colonne de texte
data['embeddings'] = data[text_column].apply(lambda x: get_embeddings(x))

# Sauvegarder les embeddings dans un nouveau fichier CSV
# Les embeddings sont généralement de longues listes de nombres, donc ils doivent être convertis en chaînes de caractères
data['embeddings'] = data['embeddings'].apply(lambda x: json.dumps(x) if x is not None else '[]')

output_csv_file_path = 'C:\\Users\\thibaut.boguszewski\\Desktop\\Tibo\\embeddings.csv'
data.to_csv(output_csv_file_path, index=False)

print(f"Embeddings saved to {output_csv_file_path}")
