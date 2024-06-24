import pandas as pd
import numpy as np
import faiss

from embedding_data.embeddings import embedding_text
from processing_data.normalizing import normalize_text

model = "aiprofilesmatching-text-embedding-3-large"

# Charger les données
file_path = "processing_data/datas/embedded_data.csv"
df = pd.read_csv(file_path)

# Charger l'index FAISS
index = faiss.read_index(
    r"C:\Users\k.simon\Projet\avv-matcher\embedding_data\index\faker_coaff.faiss"
)


def find_profiles(user_input):
    try:
        # Normaliser l'entrée utilisateur
        user_input = normalize_text(user_input)

        # Générer l'embedding de la requête
        query_embedded = embedding_text(user_input, model)
        query_embedded = np.array(query_embedded).astype("float32").reshape(1, -1)
        query_embedded = query_embedded / np.linalg.norm(query_embedded)

        # Recherche des vecteurs les plus similaires
        distances, indices = index.search(query_embedded, k=5)

        # Préparer la liste des profils trouvés
        profiles = []
        for idx in indices[0]:
            if idx < len(df):
                profile_text = df.iloc[int(idx)]["combined"]
                profiles.append(profile_text)
            else:
                print(f"Index out of bounds: {idx}")

        return profiles

    except Exception as e:
        print(f"An error occurred in find_profiles: {e}")
        return []
