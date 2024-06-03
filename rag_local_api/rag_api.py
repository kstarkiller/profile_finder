import time
import uvicorn
from fastapi import FastAPI
from load_documents import load_documents
from generate_response import generate_response
from embedding import embed_documents, retrieve_documents
from pydantic import BaseModel

DOC_PATH = r"C:\Users\k.simon\Desktop\test_og"

app = FastAPI()

@app.get("/", summary="Root endpoint", description="This is the root endpoint of the API.")
def root():
    """Returns a message to confirm that the API is running."""
    return {"message": "API is running"}

@app.get("/test", summary="Test endpoint", description="This is a test endpoint.")
def test():
    """Returns a message to confirm that the test was successful."""
    return {"message": "Test successful!"}

@app.post("/question", summary="Process question", description="This endpoint processes a question and returns a response.")
def process_question(question: str):
    """
    Process a question and return a response.

    Args:
        question (str): The question to process.

    Returns:
        dict: A dictionary containing the response generated.
    """
    # Loading the documents
    start_time = time.time()
    documents = load_documents(DOC_PATH)
    end_time = time.time()
    print(f"Documents loaded in {end_time - start_time} seconds.")

    # Embedding the documents
    start_time = time.time()
    collection = embed_documents(documents)
    end_time = time.time()
    print(f"Documents embedded in {end_time - start_time} seconds.\n")

    # Embedding the question and retrieving the documents
    start_time = time.time()
    data = retrieve_documents(question, collection)
    end_time = time.time()
    print(f"\nRAG performed in {end_time - start_time} seconds.\n")

    # Add question and retrieved data and generating response
    start_time = time.time()
    response = generate_response(data, question)
    print(f"Response: {response}")
    end_time = time.time()
    print(f"\nResponse generated in {end_time - start_time} seconds.\n\n")
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
