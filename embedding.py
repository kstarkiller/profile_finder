import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore

# Charger les données depuis le fichier Coaff_V1_cleaned.csv à la racine du projet
df = pd.read_csv('Coaff_V1_cleaned.csv')

# Colonnes textuelles à embedder
text_columns = ['PROFIL', 'Membres', 'Missions_en_cours', 'Competences', 'Stream_BT']

# Convertir toutes les valeurs des colonnes spécifiées en chaînes de caractères et combiner les colonnes
df['combined_text'] = df[text_columns].astype(str).apply(lambda x: ' '.join(x), axis=1)

# Initialisation du modèle d'embedding SentenceTransformer (à changer avec le modèle OpenAI si nécessaire)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Générer les embeddings pour les textes combinés
embeddings = model.encode(df['combined_text'].tolist()).astype(np.float32)
print(f"Embeddings shape: {embeddings.shape}")

# Créer l'index FAISS
dimension = embeddings.shape[1]  # Dimension des embeddings
index = faiss.IndexFlatL2(dimension)  # Utiliser l'index L2 (euclidean distance)
index.add(embeddings)
print("Index FAISS créé et ajouté avec les embeddings.")

# Utiliser LangChain pour gérer les embeddings et la recherche
embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

# Créer un docstore en mémoire
docstore = InMemoryDocstore({str(i): doc for i, doc in enumerate(df['combined_text'].tolist())})

# Créer un mapping de l'index vers le docstore
index_to_docstore_id = {i: str(i) for i in range(len(df))}

# Initialiser FAISS dans LangChain
faiss_index = FAISS(embedding_function=embedding_function, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)
print("FAISS index initialisé avec LangChain.")

def find_profiles(user_input):
    # Générer l'embedding de la requête
    query_embedding = model.encode([user_input]).astype(np.float32)
    print(f"Query embedding shape: {query_embedding.shape}")

    # Reshape pour s'assurer que c'est un tableau 2D
    query_embedding = query_embedding.reshape(1, -1)

    # Recherche des vecteurs les plus similaires
    distances, indices = index.search(query_embedding, k=5)
    print(f"Distances: {distances}")
    print(f"Indices: {indices}")

    # Préparer la liste des profils trouvés
    profiles = []
    for idx in indices[0]:
        profile_text = df.iloc[int(idx)]['combined_text']
        profiles.append(profile_text)
        print(f"Profile found: {profile_text}")

    return profiles
