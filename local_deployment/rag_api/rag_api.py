import time
import uvicorn
import requests
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import logging
import openlit

from llm_module.generate_response import (
    generate_ollama_response,
    generate_minai_response,
    generate_conversation_id,
)
from rag_module.embedding import embed_documents, retrieve_documents

# Vérifiez les configurations dans rag_api.py
base_path = os.path.dirname(__file__)
doc_path = os.path.join(base_path, "data", "combined")
logs_path = os.path.join(base_path, "log_module", "logs", "logs_api.log")

# Initialize OpenLit
openlit.init()

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

GPT_4O_MINI = "gpt-4o-mini"
GPT_O1_MINI = "o1-mini"
LLAMA_3_70B = "meta/meta-llama-3-70b-instruct"
CLAUDE_HAIKU = "claude-3-haiku-20240307"
COMMAND_COHERE = "command"
GEMINI_1_5_FLASH = "gemini-1.5-flash"
OLLAMA_LLM_MODEL = "llama3.1:8b"
MODEL_EMBEDDING = "nomic-embed-text:v1.5"

app = FastAPI()

# Allow CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TestInput(BaseModel):
    message: str


class ChatRequest(BaseModel):
    question: str
    history: List[dict]
    chat_id: str
    model: str


class IDrequest(BaseModel):
    model: str
    prompt: str


class TitleRequest(BaseModel):
    question: str
    chat_id: str


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
        print(doc_path)
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
            logging.error("No document found")
            raise HTTPException(status_code=500, detail="No document found")
        response = generate_ollama_response(data, input.history, input.model)
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Response generated in {end_time - start_time} seconds.\n\n")

    return {"response": response, "duration": end_time - start_time}


@app.post(
    "/new_chat_id",
    summary="New chat ID",
    description="This endpoint generates a new chat ID.",
)
def new_chat_id(input: IDrequest):
    """Generates a new chat ID.
    This endpoint generates a new chat ID for a new conversation.

    Args:
        model (str): The model to use for the generation.
        prompt (str): The prompt for the new id.

    Returns:
        new_id (str): The new chat ID.
    """
    new_id = generate_conversation_id(input.model, input.prompt)

    return {"new_id": new_id}


@app.post(
    "/minai_chat",
    summary="Process question",
    description="This endpoint processes a question and returns a response with perplexity.",
)
def process_question_minai(input: ChatRequest):
    """
    Process a question and return a response.

    Args:
        question (str): The question to process.

    Returns:
        dict: A dictionary containing the response generated.
    """
    # Embed the question and retrieve the documents
    embedding_start_time = time.time()
    try:
        data = retrieve_documents(input.question, MODEL_EMBEDDING)
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    embedding_end_time = time.time()
    logging.info(
        f"RAG performed in {embedding_end_time - embedding_start_time} seconds.\n"
    )
    # Add question and retrieved data then generate a response
    llm_start_time = time.time()
    try:
        if data is None:
            logging.error("No document found")
            raise HTTPException(status_code=500, detail="No document found")
        response = generate_minai_response(
            data[0], input.chat_id, input.history, input.model
        )
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    llm_end_time = time.time()
    logging.info(f"Response generated in {llm_end_time - llm_start_time} seconds.\n\n")

    duration = round(llm_end_time - llm_start_time, 2)
    return {"response": response, "duration": duration}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
