import os
import time
import logging

# import requests
import uvicorn
import mlflow
from datetime import timedelta
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import List

from auth import create_access_token, get_user
from llm_module.generate_response import (
    generate_ollama_response,
    generate_minai_response,
    generate_conversation_id,
)
from rag_module.embedding import retrieve_documents
from rag_cd import delete_temp_files, process_file
from docker_check import is_running_in_docker

venv = is_running_in_docker()

# Paths definition
base_path = os.path.dirname(__file__)
paths = {
    "logs": os.path.join(base_path, "log_module", "logs", "api.log"),
    "temp_combined": os.path.join(base_path, "data", "combined", "_temp"),
    "collection": os.path.join(base_path, "data", "chroma", "docs"),
}

# Logging module configuration
logging.basicConfig(
    filename=paths["logs"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Constants
GPT_4O_MINI = "gpt-4o-mini"
MODEL_EMBEDDING = "nomic-embed-text:v1.5"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


class TestInput(BaseModel):
    message: str


class ChatRequest(BaseModel):
    service_type: str
    question: str
    history: List[dict]
    chat_id: str
    model: str


class IDrequest(BaseModel):
    model: str
    prompt: str


class Token(BaseModel):
    access_token: str
    token_type: str


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Profile Finder API",
        version="1.0.0",
        description="API for managing profiles and processing questions.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get(
    "/", summary="Root endpoint", description="This is the root endpoint of the API."
)
def root():
    return {"message": "API is running"}


@app.post("/test", summary="Test endpoint", description="This is a test endpoint.")
def test(input: TestInput):
    return {"message": input.message + " Success"}


@app.get(
    "/token",
    summary="Get token",
    description="This endpoint retrieves a token for the user.",
    response_model=Token,
)
async def login(username: str):
    email = get_user(username)
    if not email:
        raise HTTPException(status_code=400, detail="Incorrect username")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/file",
    summary="Store file",
    description="This endpoint stores a file in the database.",
)
async def storing_file(file: UploadFile = File(...)):
    try:
        result_validation_temp = process_file(file, "temp")
        if result_validation_temp[1] <= 7:
            result_validation_perm = process_file(file, "perm")

        mlflow.set_tracking_uri(f"http://{venv['mf_host']}:{venv['mf_port']}")
        mlflow.set_experiment("Profile Finder RAG Metrics")

        with mlflow.start_run():
            if file.filename != "test_file.txt":
                mlflow.log_param("file_name", file.filename)
                mlflow.log_param("date", time.strftime("%Y-%m-%d %H:%M:%S"))

                mlflow.log_metric("False rate", result_validation_temp[1])
                mlflow.log_artifact("Result table", result_validation_temp[0])

                result_validation_path = os.path.join(
                    paths["temp_combined"], "result_validation.csv"
                )
                result_validation_perm[0].to_csv(result_validation_path, index=False)
                mlflow.log_artifact(result_validation_path)

        mlflow.end_run()

        delete_temp_files(file)

    except Exception as e:
        raise Exception(f"Error: {str(e)}")


@app.post(
    "/chat",
    summary="Process question and return response",
    description="This endpoint processes a question and returns a response with ollama.",
)
def process_question(input: ChatRequest):
    start_time = time.time()
    try:
        data = retrieve_documents(
            paths["collection"], "perm", input.question, MODEL_EMBEDDING
        )
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"RAG performed in {end_time - start_time} seconds.\n")

    start_time = time.time()
    try:
        if data is None:
            logging.error("No document found")
            raise HTTPException(status_code=500, detail="No document found")
        if input.service_type == "ollama":
            response = generate_ollama_response(data, input.history, input.model)
        elif input.service_type == "minai":
            response = generate_minai_response(
                data[0], input.chat_id, input.history, input.model
            )
        else:
            raise HTTPException(status_code=500, detail="Incorrect service type")
    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Response generated in {end_time - start_time} seconds.\n\n")

    if input.chat_id != "chat_id123":
        mlflow.set_tracking_uri(f"http://{venv['mf_host']}:{venv['mf_port']}")
        mlflow.set_experiment("Profile Finder Chat Metrics")

        run = mlflow.start_run()
        try:
            mlflow.log_param("service_type", input.service_type)
            mlflow.log_param("date", time.strftime("%Y-%m-%d %H:%M:%S"))
            mlflow.log_param("chat_id", input.chat_id)
            mlflow.log_param("model", input.model)
            mlflow.log_metric("response_time", round(end_time - start_time, 2))
        finally:
            mlflow.end_run()

    return {"response": response, "duration": end_time - start_time}


@app.post(
    "/chat/id",
    summary="New chat ID",
    description="This endpoint generates a new chat ID.",
)
def new_chat_id(input: IDrequest):
    """
    Generate a new conversation ID based on the model and prompt provided.

    Args:
        input (IDrequest): Model and prompt for the conversation ID
        current_user (dict): Current user information

    Returns:
        dict: New conversation ID

    Raises:
        HTTPException: Exception HTTP 401 Unauthorized if the token is invalid or the user does not exist
    """
    new_id = generate_conversation_id(input.model, input.prompt)

    return {"new_id": new_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
