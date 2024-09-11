import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from generate_response import generate_response
from embedding import embed_documents, retrieve_documents

if os.name == 'posix':
    DOC_PATH = r"/home/kevin/simplon/briefs/avv-matcher/rag_local_api/sources"
else:
    DOC_PATH = r"C:\Users\k.simon\Projet\avv-matcher\rag_local_api\sources"

MODEL_LLM = "llama3.1:8b"
MODEL_EMBEDDING = "all-minilm:33m"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Root endpoint", description="This is the root endpoint of the API.")
def root():
    """Returns a message to confirm that the API is running."""
    return {"message": "API is running"}

class TestInput(BaseModel):
    message: str

@app.post("/test", summary="Test endpoint", description="This is a test endpoint.")
def test(input: TestInput):
    """Returns the user input as a response.
    This is a test endpoint to check if the API is working properly.    
    """
    return {"message": input.message + " Success"}

@app.post("/embedding", summary="Embedding endpoint", description="This is the question endpoint.")
def embedding():
    """Embeds the documents and returns the collection.
    This endpoint embeds the documents using the all-minilm:33m model and returns the collection.

    Args:
        documents (list): A list of documents to embed.

    Returns:
        dict: A dictionary containing the collection of embedded documents.
    """
    # Embedding the documents
    start_time = time.time()
    try:
        collection = embed_documents(DOC_PATH, MODEL_EMBEDDING)
    except Exception as e:
        print(f"Error embedding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    print(f"Documents embedded in {end_time - start_time} seconds.\n")

    return {"collection": collection}

@app.post("/question", summary="Process question", description="This endpoint processes a question and returns a response.")
def process_question(question: str):
    """
    Process a question and return a response.

    Args:
        question (str): The question to process.

    Returns:
        dict: A dictionary containing the response generated.
    """
    # Embedding the question and retrieving the documents
    start_time = time.time()
    try:
        data = retrieve_documents(question, MODEL_EMBEDDING)
    except Exception as e:
        print(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    print(f"\nRAG performed in {end_time - start_time} seconds.\n")

    # Add question and retrieved data and generating response
    start_time = time.time()
    try:
        response = generate_response(data, question, MODEL_LLM)
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    print(f"Response: {response}" + "success")
    end_time = time.time()
    print(f"\nResponse generated in {end_time - start_time} seconds.\n\n")
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)