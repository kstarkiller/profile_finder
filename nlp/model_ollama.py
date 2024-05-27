import time

from load_documents import load_documents
from generate_response import generate_response
from embedding import embed_documents, embed_question

# Chargement des documents
start_time = time.time()
documents = load_documents(r"C:\Users\k.simon\Desktop\test_loads")
end_time = time.time()
print(f"Documents chargés en {end_time - start_time} secondes.\n\n")

# Embedding des documents
start_time = time.time()
embeded_documents = embed_documents(documents)
end_time = time.time()
print(f"Documents embeddés en {end_time - start_time} secondes.\n\n")

# Entrée et embedding du prompt
question = input("Enter your question: ")
start_time = time.time()
embeded_question = embed_question(question)
embed_end_time = time.time()
print(f"Question embeddée en {end_time - start_time} secondes.\n\n")

# Génération de la réponse
start_time = time.time()
response = generate_response(embeded_question, embeded_documents)
end_time = time.time()
print(f"\nRéponse générée en {end_time - start_time} secondes.\n\n")