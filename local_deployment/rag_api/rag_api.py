import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import logging

from llm_module.generate_response import (
    generate_ollama_response,
    generate_perplexity_response,
)
from rag_module.embedding import embed_documents, retrieve_documents

if os.name == "posix":
    doc_path = r"/home/kevin/simplon/briefs/avv-matcher/local_deployment/rag_api/data/sources"
    logs_path = (
        r"/home/kevin/simplon/briefs/avv-matcher/local_deployment/rag_api/log_module/logs/logs_api.log"
    )
else:
    doc_path = r"C:\\Users\\k.simon\\Projet\\avv-matcher\\local_deployment\\rag_api\\data\\sources"
    logs_path = (
        r"C:\\Users\\k.simon\\Projet\\avv-matcher\\local_deployment\\rag_api\\log_module\\logs\\logs_api.log"
    )

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

MODEL_LLM = "llama3.1:8b"
MODEL_EMBEDDING = "nomic-embed-text:latest"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TestInput(BaseModel):
    message: str


class ChatRequest(BaseModel):
    question: str
    history: List[dict]


@app.get(
    "/", summary="Root endpoint", description="This is the root endpoint of the API."
)
def root():
    """Returns a message to confirm that the API is running."""
    return {"message": "API is running"}


@app.post("/test", summary="Test endpoint", description="This is a test endpoint.")
def test(input: TestInput):
    """Returns the user input as a response.
    This is a test endpoint to check if the API is working properly.
    """
    return {"message": input.message + " Success"}


@app.post(
    "/embedding",
    summary="Embedding endpoint",
    description="This is the question endpoint.",
)
def embedding():
    """Embeds the documents and returns the collection.
    This endpoint embeds the documents and returns the collection.

    Args:
        documents (list): A list of documents to embed.

    Returns:
        dict: A dictionary containing the collection of embedded documents.
    """
    # Embedding the documents
    start_time = time.time()
    try:
        collection = embed_documents(doc_path, MODEL_EMBEDDING)
    except Exception as e:
        logging.error(f"Error embedding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Documents embedded in {end_time - start_time} seconds.\n")

    return {"collection": collection}


@app.post(
    "/ollama_chat",
    summary="Process question",
    description="This endpoint processes a question and returns a response with ollama.",
)
def process_question_ollama(input: ChatRequest):
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
        data = retrieve_documents(input.question, MODEL_EMBEDDING)
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"RAG performed in {end_time - start_time} seconds.\n")

    # Add question and retrieved data and generating response
    start_time = time.time()
    try:
        if data is None:
            logging.error("Aucun document trouvé")
            raise HTTPException(status_code=500, detail="Aucun document trouvé")
        response = generate_ollama_response(data, input.question, MODEL_LLM)
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Response generated in {end_time - start_time} seconds.\n\n")

    return {"response": response}


@app.post(
    "/perplexity_chat",
    summary="Process question",
    description="This endpoint processes a question and returns a response with perplexity.",
)
def process_question_perplexity(input: ChatRequest):
    """
    Process a question and return a response.

    Args:
        question (str): The question to process.

    Returns:
        dict: A dictionary containing the response generated.
    """

    # Embed the question and retrieve the documents
    start_time = time.time()
    try:
        data = retrieve_documents(input.question, MODEL_EMBEDDING)
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"RAG performed in {end_time - start_time} seconds.\n")

    # Add question and retrieved data then generate a response
    start_time = time.time()
    try:
        if data is None:
            logging.error("Aucun document trouvé")
            raise HTTPException(status_code=500, detail="Aucun document trouvé")
        response = generate_perplexity_response(
            data, input.history, "llama-3.1-70b-instruct"
        )
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Response generated in {end_time - start_time} seconds.\n\n")

    return {"response": response}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
