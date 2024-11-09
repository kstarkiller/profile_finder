import os
import time
import logging
import requests
import uvicorn
import mlflow
from datetime import timedelta
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List

from auth import create_access_token, get_user, get_current_user
from llm_module.generate_response import (
    generate_ollama_response,
    generate_minai_response,
    generate_conversation_id,
)
from rag_module.embedding import embed_documents, retrieve_documents, delete_collection
from data.pre_processing import insert_profiles
from data.store_file import store_file, download_files
from data.get_skills import get_skills
from data.create_fixtures import create_fixtures
import test_unitaires.test_embedding as test_embedding
import test_unitaires.test_load_documents as test_load_documents
import test_unitaires.test_ollama as test_ollama
from perf_validation import run_validation
from docker_check import is_running_in_docker

# Paths definition
base_path = os.path.dirname(__file__)
paths = {
    "logs": os.path.join(base_path, "log_module", "logs", "logs_api.log"),
    "sources": os.path.join(base_path, "data", "sources_files"),
    "fixtures": os.path.join(base_path, "data", "fixtures"),
    "combined": os.path.join(base_path, "data", "combined"),
    "collection": os.path.join(base_path, "data", "chroma"),
    "temp_files": os.path.join(base_path, "data", "sources_files", "_temp"),
    "temp_fixtures": os.path.join(base_path, "data", "fixtures", "_temp"),
    "temp_combined": os.path.join(base_path, "data", "combined", "_temp"),
    "temp_collection": os.path.join(base_path, "data", "chroma", "_temp"),
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


class TitleRequest(BaseModel):
    question: str
    chat_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

venv = is_running_in_docker()

def create_directories():
    for path in paths.values():
        if not os.path.exists(path):
            os.makedirs(path)
    os.replace(
        os.path.join(paths["sources"], "Coaff_V1.xlsx"),
        os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
    )
    os.replace(
        os.path.join(paths["sources"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"),
        os.path.join(
            paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
        ),
    )
    os.replace(
        os.path.join(paths["sources"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"),
        os.path.join(paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"),
    )


@app.get(
    "/", summary="Root endpoint", description="This is the root endpoint of the API."
)
def root():
    return {"message": "API is running"}


@app.post("/test", summary="Test endpoint", description="This is a test endpoint.")
def test(input: TestInput):
    return {"message": input.message + " Success"}

@app.get("/token",
    summary="Get token",
    description="This endpoint retrieves a token for the user.",
    response_model=Token)
async def login(username: str):
    email = get_user(username)
    if not email:
        raise HTTPException(
            status_code=400, detail="Incorrect username"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post(
    "/file",
    summary="Store file",
    description="This endpoint stores a file in the database.",
)
async def storing_file(file: UploadFile = File(...)):
    create_directories()
    time.sleep(1)
    try:
        file_path = os.path.join(paths["temp_files"], file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        progress["percentage"] = 12
        time.sleep(1)

        result_storing = store_file(
            file_path,
            venv["mongo_user"],
            venv["mongo_pwd"],
            venv["mongo_host"],
            venv["mongo_port"],
            venv["mongo_db"],
        )
        progress["percentage"] = 19
        time.sleep(1)

        result_download = download_files(
            venv["mongo_user"],
            venv["mongo_pwd"],
            venv["mongo_host"],
            venv["mongo_port"],
            venv["mongo_db"],
            "temp",
        )
        progress["percentage"] = 28
        time.sleep(1)

        result_skills = get_skills(
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            ),
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
            os.path.join(paths["temp_files"], "descriptions_uniques.txt"),
            os.path.join(paths["temp_files"], "profils_uniques.txt"),
        )
        progress["percentage"] = 32
        time.sleep(1)

        result_fixtures = create_fixtures(
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            ),
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
            os.path.join(
                paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
            ),
            os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv"),
            os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv"),
            os.path.join(paths["temp_fixtures"], "fixtures_certs.csv"),
        )
        progress["percentage"] = 41
        time.sleep(1)

        response = requests.delete(
            f"http://{venv['db_api_host']}:{venv['db_api_port']}/profiles",
            json={"type": "temp"},
        )
        response.raise_for_status()

        result_insert = insert_profiles(
            venv["db_api_host"],
            venv["db_api_port"],
            os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv"),
            os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv"),
            os.path.join(paths["temp_fixtures"], "fixtures_certs.csv"),
            os.path.join(paths["temp_combined"], "combined_result.csv"),
            "temp",
        )
        progress["percentage"] = 53
        delete_collection(paths["temp_collection"], "temp")
        result_embed = embed_documents(
            paths["temp_collection"], "temp", MODEL_EMBEDDING
        )
        progress["percentage"] = 60
        time.sleep(1)

        if file.filename != "test_file.txt":
            test_embedding
            test_load_documents
            test_ollama
            progress["percentage"] = 62
            time.sleep(1)

        result_validation = run_validation(
            paths["temp_collection"],
            "temp",
            os.path.join(paths["temp_combined"], "combined_result.csv"),
            MODEL_EMBEDDING,
            GPT_4O_MINI,
        )

        progress["percentage"] = 71
        time.sleep(1)

        result_perm_dl = download_files(
            venv["mongo_user"],
            venv["mongo_pwd"],
            venv["mongo_host"],
            venv["mongo_port"],
            venv["mongo_db"],
            "perm",
        )
        progress["percentage"] = 78
        time.sleep(1)

        result_perm_skills = get_skills(
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            ),
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
            os.path.join(paths["sources"], "descriptions_uniques.txt"),
            os.path.join(paths["sources"], "profils_uniques.txt"),
        )
        progress["percentage"] = 82
        time.sleep(1)

        result_perm_fixtures = create_fixtures(
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            ),
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
            os.path.join(
                paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
            ),
            os.path.join(paths["fixtures"], "fixtures_psarm.csv"),
            os.path.join(paths["fixtures"], "fixtures_coaff.csv"),
            os.path.join(paths["fixtures"], "fixtures_certs.csv"),
        )
        progress["percentage"] = 89
        time.sleep(1)

        response = requests.delete(
            f"http://{venv['db_api_host']}:{venv['db_api_port']}/profiles",
            json={"type": "perm"},
        )
        response.raise_for_status()

        result_perm_profiles = insert_profiles(
            venv["db_api_host"],
            venv["db_api_port"],
            os.path.join(paths["fixtures"], "fixtures_psarm.csv"),
            os.path.join(paths["fixtures"], "fixtures_coaff.csv"),
            os.path.join(paths["fixtures"], "fixtures_certs.csv"),
            os.path.join(paths["combined"], "combined_result.csv"),
            "perm",
        )
        progress["percentage"] = 96
        time.sleep(1)

        delete_collection(paths["collection"], "perm")
        docs = embed_documents(paths["collection"], "perm", MODEL_EMBEDDING)
        progress["percentage"] = 100
        time.sleep(1)

        mlflow.set_tracking_uri(f"http://{venv['mf_host']}:{venv['mf_port']}")
        mlflow.set_experiment("Profile Finder RAG Metrics")

        with mlflow.start_run():
            if file.filename != "test_file.txt":
                mlflow.log_param("file_name", file.filename)
                mlflow.log_param("date", time.strftime("%Y-%m-%d %H:%M:%S"))
                mlflow.log_artifact(
                    os.path.join(paths["temp_combined"], "combined_result.csv")
                )
            
                mlflow.log_metric("accuracy", f"{result_validation[1]:.2f%}")
                mlflow.log_metric("false_rate", f"{result_validation[1]:.2f%}")

                result_validation_path = os.path.join(
                    paths["temp_combined"], "result_validation.csv"
                )
                result_validation[0].to_csv(result_validation_path, index=False)
                mlflow.log_artifact(result_validation_path)

        mlflow.end_run()

        delete_collection(paths["temp_collection"], "temp")

        if file.filename != "test_file.txt":
            os.remove(os.path.join(paths["temp_files"], "Coaff_V1.xlsx"))
            os.remove(
                os.path.join(
                    paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
                )
            )
            os.remove(
                os.path.join(
                    paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
                )
            )
        else:
            os.remove(os.path.join(paths["temp_files"], "test_file.txt"))
            os.replace(
                os.path.join(paths["temp_files"], "Coaff_V1.xlsx"),
                os.path.join(paths["sources"], "Coaff_V1.xlsx"),
            )
            os.replace(
                os.path.join(
                    paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
                ),
                os.path.join(
                    paths["sources"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
                ),
            )
            os.replace(
                os.path.join(
                    paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
                ),
                os.path.join(
                    paths["sources"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
                ),
            )
        if os.path.exists(
            os.path.join(paths["temp_files"], "descriptions_uniques.txt")
        ):
            os.remove(os.path.join(paths["temp_files"], "descriptions_uniques.txt"))
        if os.path.exists(os.path.join(paths["temp_files"], "profils_uniques.txt")):
            os.remove(os.path.join(paths["temp_files"], "profils_uniques.txt"))
        if os.path.exists(os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv")):
            os.remove(os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv"))
        if os.path.exists(os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv")):
            os.remove(os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv"))
        if os.path.exists(os.path.join(paths["temp_fixtures"], "fixtures_certs.csv")):
            os.remove(os.path.join(paths["temp_fixtures"], "fixtures_certs.csv"))
        if os.path.exists(os.path.join(paths["temp_combined"], "combined_result.csv")):
            os.remove(os.path.join(paths["temp_combined"], "combined_result.csv"))

    except Exception as e:
        progress["percentage"] = 0
        raise Exception(f"Error: {str(e)}")


@app.get(
    "/progress",
    summary="Get progress",
    description="This endpoint retrieves the progress of the current request.",
)
def get_progress():
    global progress
    return progress


@app.get(
    "/file",
    summary="Get file",
    description="This endpoint retrieves a file from the database.",
)
def getting_file():
    try:
        result = download_files(
            venv["mongo_user"],
            venv["mongo_pwd"],
            venv["mongo_host"],
            venv["mongo_port"],
            venv["mongo_db"],
            "perm",
        )
        return {"message": result}
    except Exception as e:
        return {"message": f"Error retrieving file: {str(e)}"}


@app.get(
    "/profiles",
    summary="Insert profiles",
    description="This endpoint inserts profiles into the database if not already exist.",
)
def storing_profiles():
    try:
        response = requests.get(
            f"http://{venv['db_api_host']}:{venv['db_api_port']}/profiles",
            params={"type": "perm"},
        )
        response.raise_for_status()
        profiles = response.json()
        if len(profiles["profiles"]) == 0:
            result = insert_profiles(
                venv["db_api_host"],
                venv["db_api_port"],
                os.path.join(paths["fixtures"], "fixtures_coaff.csv"),
                os.path.join(paths["fixtures"], "fixtures_psarm.csv"),
                os.path.join(paths["fixtures"], "fixtures_certs.csv"),
                os.path.join(paths["combined"], "combined_result.csv"),
                "perm",
            )
            return {f"message": f"{result} profiles added to the database"}
        else:
            return {"message": "Database already contains profiles"}
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)


@app.delete(
    "/profiles",
    summary="Delete profiles",
    description="This endpoint truncates the table in the database.",
)
def truncate_table():
    try:
        response = requests.delete(
            f"http://{venv['db_api_host']}:{venv['db_api_port']}/profiles",
            params={"type": "perm"},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("HTTP error occurred:", err)


@app.post(
    "/embed", summary="Embedding endpoint", description="This is the question endpoint."
)
def embedding():
    start_time = time.time()
    try:
        result = embed_documents(paths["collection"], "perm", MODEL_EMBEDDING)
    except Exception as e:
        logging.error(f"Error embedding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    end_time = time.time()
    logging.info(f"Documents embedded in {end_time - start_time} seconds.\n")
    return {"collection": result}


@app.post(
    "/chat",
    summary="Process question and return response",
    description="This endpoint processes a question and returns a response with ollama.",
)
def process_question(input: ChatRequest, current_user: dict = Depends(get_current_user)):
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

    mlflow.set_tracking_uri(f"http://{venv['mf_host']}:{venv['mf_port']}")
    mlflow.set_experiment("Profile Finder Chat Metrics")

    run = mlflow.start_run()
    try:
        mlflow.log_param("service_type", input.service_type)
        mlflow.log_param("date", time.strftime("%Y-%m-%d %H:%M:%S"))
        mlflow.log_param("chat_id", input.chat_id)
        mlflow.log_param("model", input.model)
        mlflow.log_metric("response_time", end_time - start_time)
    finally:
        mlflow.end_run()

    return {"response": response, "duration": end_time - start_time}


@app.post(
    "/chat/id",
    summary="New chat ID",
    description="This endpoint generates a new chat ID.",
)
def new_chat_id(input: IDrequest, current_user: dict = Depends(get_current_user)):
    new_id = generate_conversation_id(input.model, input.prompt)
    return {"new_id": new_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
