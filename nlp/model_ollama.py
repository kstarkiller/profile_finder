import time
import uvicorn
from fastapi import FastAPI

from load_documents import load_documents
from generate_response import generate_response
from embedding import embed_documents, retrieve_documents


app = FastAPI()

@app.get("/")
def root():
    return {"message": "API is running"}

@app.post("/question")
def process_question(question: str):
    # Chargement des documents
    start_time = time.time()
    documents = load_documents(r"C:\Users\k.simon\Desktop\test_og")
    end_time = time.time()
    print(f"Documents chargés en {end_time - start_time} secondes.")

    # Embedding des documents
    start_time = time.time()
    collection = embed_documents(documents)
    end_time = time.time()
    print(f"Documents embeddés en {end_time - start_time} secondes.\n")

    # Entrée et embedding du prompt
    # question = input("Enter your question: ")
    start_time = time.time()
    data = retrieve_documents(question, collection)
    end_time = time.time()
    print(f"\nRAG effectué en {end_time - start_time} secondes.\n")

    # Génération de la réponse
    start_time = time.time()
    response = generate_response(data, question)
    print(f"Response: {response}")
    end_time = time.time()
    print(f"\nRéponse générée en {end_time - start_time} secondes.\n\n")
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)