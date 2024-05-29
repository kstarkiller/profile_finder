import time
import os
import psutil

from load_documents import load_documents
from generate_response import generate_response
from embedding import embed_documents, retrieve_documents

# Chargement des documents
start_time = time.time()
documents = load_documents(r"C:\Users\k.simon\Desktop\test_loads")
end_time = time.time()
print(f"Documents chargés en {end_time - start_time} secondes.\n\n")

# Embedding des documents
start_time = time.time()
collection = embed_documents(documents)
end_time = time.time()
print(f"Documents embeddés en {end_time - start_time} secondes.\n\n")

# Entrée et embedding du prompt
question = input("Enter your question: ")
start_time = time.time()
data = retrieve_documents(question, collection)
end_time = time.time()
print(f"RAG effectué en {end_time - start_time} secondes.\n\n")

# Génération de la réponse
start_time = time.time()
response = generate_response(data, question)
end_time = time.time()
print(f"\nRéponse générée en {end_time - start_time} secondes.\n\n")

# Afficher le pourcentage CPU et mémoire utilisé
process = psutil.Process(os.getpid())
print(f"CPU: {process.cpu_percent()}%")
print(f"Memory: {process.memory_info().rss / 1024 / 1024} MB")