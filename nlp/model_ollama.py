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
    # Loading the documents
    start_time = time.time()
    documents = load_documents(r"C:\Users\k.simon\Desktop\test_og")
    end_time = time.time()
    print(f"Documents loaded in {end_time - start_time} seconds.")

    # Embedding the documents
    start_time = time.time()
    collection = embed_documents(documents)
    end_time = time.time()
    print(f"Documents embedded in {end_time - start_time} seconds.\n")

    # Embedding the prompt and retrieving the documents
    start_time = time.time()
    data = retrieve_documents(question, collection)
    end_time = time.time()
    print(f"\nRAG performed in {end_time - start_time} seconds.\n")

    # Generating the response
    start_time = time.time()
    response = generate_response(data, question)
    print(f"Response: {response}")
    end_time = time.time()
    print(f"\nResponse generated in {end_time - start_time} seconds.\n\n")
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
