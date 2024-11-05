import time
import uvicorn
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
import logging

from llm_module.generate_response import (
    generate_ollama_response,
    generate_minai_response,
    generate_conversation_id,
)
from rag_module.embedding import embed_documents, retrieve_documents
from data.pre_processing import insert_profiles
from data.store_file import store_file, download_files
from data.get_skills import get_skills
from data.create_fixtures import create_fixtures
from docker_check import is_running_in_docker

# Paths' definition
base_path = os.path.dirname(__file__)
logs_path = os.path.join(base_path, "log_module", "logs", "logs_api.log")
temp_files = os.path.join(base_path, "data", "temp_files")
temp_sources = os.path.join(base_path, "data", "downloaded_files")
sources = os.path.join(base_path, "data", "source_files")
fixtures_coaff = os.path.join(base_path, "fixtures", "fixtures_coaff.csv")
fixtures_psarm = os.path.join(base_path, "fixtures", "fixtures_psarm.csv")
fixtures_certs = os.path.join(base_path, "fixtures", "fixtures_certs.csv")
temp_fixtures_coaff = os.path.join(base_path, "temp_fixtures", "fixtures_coaff.csv")
temp_fixtures_psarm = os.path.join(base_path, "temp_fixtures", "fixtures_psarm.csv")
temp_fixtures_certs = os.path.join(base_path, "temp_fixtures", "fixtures_certs.csv")
combined = os.path.join(base_path, "data", "combined")
temp_combined = os.path.join(base_path, "data", "temp_combined")
temp_psarm = os.path.join(
    base_path, temp_sources, "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
)
temp_coaff = os.path.join(base_path, temp_sources, "Coaff_V1.xlsx")
temp_certs = os.path.join(
    base_path, temp_sources, "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
)
temp_descriptions_uniques = os.path.join(
    base_path, temp_sources, "descriptions_uniques.txt"
)
temp_profiles_uniques = os.path.join(base_path, temp_sources, "profils_uniques.txt")
collection= os.path.join(base_path, "data", "chroma")
temp_collection = os.path.join(base_path, "data", "temp_chroma")

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


db_api_host, db_api_port, mongo_host, mongo_port, mongo_user, mongo_pwd, mongo_db = (
    is_running_in_docker()
)


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
    "/store_file",
    summary="Store file",
    description="This endpoint stores a file in the database.",
)
def storing_file(file: UploadFile = File(...)):
    """Stores a file in the database.

    Args:
        file (upload): The file to store.
        type (str): The type of the file.

    Returns:
        dict: A dictionary containing the success message.
    """
    try:
        # Temporally store the file locally
        file_path = os.path.join(temp_files, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        yield {"message": "File stored temporarily", "percentage": 10}
    except Exception as e:
        return {"message": f"Error temporary storing file: {str(e)}"}

    try:
        # Store the file in the database
        result = store_file(
            file_path, mongo_user, mongo_pwd, mongo_host, mongo_port, mongo_db
        )
        yield {"message": result, "percentage": 20}
    except Exception as e:
        return {"message": f"Error storing file: {str(e)}"}

    # Remove the temporally stored file
    os.remove(file_path)

    try:
        # Download the files to add it to the rag
        result = download_files(mongo_user, mongo_pwd, mongo_host, mongo_port, mongo_db)
        yield {"message": result, "percentage": 30}
    except Exception as e:
        return {"message": f"Error downloading file: {str(e)}"}

    try:
        # Get the skills from the files
        result = get_skills(temp_psarm, temp_coaff, temp_descriptions_uniques, temp_profiles_uniques)
        yield {"message": f"{result}", "percentage": 40}
    except Exception as e:
        return {"message": f"Error getting skills: {str(e)}"}

    try:
        # Create the fixtures
        result = create_fixtures(
            temp_psarm,
            temp_coaff,
            temp_certs,
            temp_fixtures_psarm,
            temp_fixtures_coaff,
            temp_fixtures_certs,
        )
        yield {"message": f"{result}", "percentage": 50}
    except Exception as e:
        return {"message": f"Error creating fixtures: {str(e)}"}
    
    try:
        # Preprocess the data and insert the profiles into the database
        result = insert_profiles(db_api_host, db_api_port, temp_fixtures_coaff, temp_fixtures_psarm, temp_fixtures_certs, temp_combined)
        yield {"message": f"{result}", "percentage": 60}
    except Exception as e:
        return {"message": f"Error inserting profiles: {str(e)}"}
    
    try:
        # Embed the documents
        collection = embed_documents(temp_collection, MODEL_EMBEDDING)
        yield {"message": f"{len(collection)} documents embedded", "percentage": 70}
    except Exception as e:
        return {"message": f"Error embedding documents: {str(e)}"}
    
    try:
        # Replace the old collection with the new one as everything was successful
        os.replace(temp_collection, collection)
        os.replace(temp_combined, combined)
        os.replace(temp_fixtures_coaff, fixtures_coaff)
        os.replace(temp_fixtures_psarm, fixtures_psarm)
        os.replace(temp_fixtures_certs, fixtures_certs)
        os.replace(temp_sources, sources)
        os.rename(temp_collection, collection)
        os.rename(temp_combined, combined)
        os.rename(temp_fixtures_coaff, fixtures_coaff)
        os.rename(temp_fixtures_psarm, fixtures_psarm)
        os.rename(temp_fixtures_certs, fixtures_certs)
        os.rename(temp_sources, sources)
        yield {"message": "Files replaced successfully", "percentage": 90}
    except Exception as e:
        return {"message": f"Error replacing files: {str(e)}"}


@app.get(
    "/get_file",
    summary="Get file",
    description="This endpoint retrieves a file from the database.",
)
def getting_file():
    """Retrieves a file from the database.

    Args:
        filename (str): The name of the file to retrieve.
        type (str): The type of the file.

    Returns:
        dict: A dictionary containing the success message.
    """
    try:
        result = download_files(mongo_user, mongo_pwd, mongo_host, mongo_port, mongo_db)
        return {"message": result}
    except Exception as e:
        return {"message": f"Error retrieving file: {str(e)}"}


@app.post(
    "/store_profiles",
    summary="Insert profiles",
    description="This endpoint inserts profiles into the database if not already exist.",
)
def storing_profiles():
    try:
        response = requests.get(f"http://{db_api_host}:{db_api_port}/get_profiles")
        response.raise_for_status()
        profiles = response.json()
        # Check if profiles is an empty list
        if len(profiles["profiles"]) == 0:
            result = insert_profiles(db_api_host, db_api_port)
            return {f"message": f"{result} profiles added to the database"}
        else:
            return {"message": "Database already contains profiles"}
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)


@app.post(
    "/truncate_table",
    summary="Truncate table",
    description="This endpoint truncates the table in the database.",
)
def truncate_table():
    try:
        response = requests.post(f"http://{db_api_host}:{db_api_port}/truncate_table")
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)


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
        collection = embed_documents(collection, MODEL_EMBEDDING)
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
        data = retrieve_documents(collection, input.question, MODEL_EMBEDDING)
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
        data = retrieve_documents(collection, input.question, MODEL_EMBEDDING)
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
