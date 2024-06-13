import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from load_documents import load_documents
from generate_response import generate_response
from embedding import embed_documents, retrieve_documents
from pydantic import BaseModel

DOC_PATH = "C:\\Users\\thibaut.boguszewski\\Desktop\\Tibo\\test API"
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8503",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    """Returns the user input as a response."""
    return {"message": input.message + " Success"}

@app.post("/question", summary="Process question", description="This endpoint processes a question and returns a response.")
def process_question(question: TestInput):
    """
    Process a question and return a response.

    Args:
        question (str): The question to process.

    Returns:
        dict: A dictionary containing the response generated.
    """
    # Loading the documents
    start_time = time.time()
    try:
        documents = load_documents(DOC_PATH)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    end_time = time.time()
    print(f"Documents loaded in {end_time - start_time} seconds.")

    # Embedding the documents
    start_time = time.time()
    collection = embed_documents(documents)
    end_time = time.time()
    print(f"Documents embedded in {end_time - start_time} seconds.\n")

    # Embedding the question and retrieving the documents
    start_time = time.time()
    data = retrieve_documents(question.message, collection)  # Pass the message string directly
    end_time = time.time()
    print(f"\nRAG performed in {end_time - start_time} seconds.\n")

    # Add question and retrieved data and generating response
    start_time = time.time()
    try:
        response = generate_response(data, question.message)  # Pass the message string directly
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    print(f"Response: {response}" + "success")
    end_time = time.time()
    print(f"\nResponse generated in {end_time - start_time} seconds.\n\n")
    
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)