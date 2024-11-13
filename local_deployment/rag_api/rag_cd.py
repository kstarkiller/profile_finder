import os
import requests
import logging

from data.store_file import store_file, download_files
from data.get_skills import get_skills
from data.create_fixtures import create_fixtures
from data.pre_processing import insert_profiles
import test_unitaires.test_embedding as test_embedding
import test_unitaires.test_load_documents as test_load_documents
import test_unitaires.test_ollama as test_ollama
from rag_module.embedding import embed_documents, delete_collection
from perf_validation import run_validation
from docker_check import is_running_in_docker

venv = is_running_in_docker()

GPT_4O_MINI = "gpt-4o-mini"
MODEL_EMBEDDING = "nomic-embed-text:v1.5"

# Paths definition
base_path = os.path.dirname(__file__)
paths = {
    "logs": os.path.join(base_path, "log_module", "logs", "rag_ci.log"),
    "sources": os.path.join(base_path, "data", "sources_files"),
    "fixtures": os.path.join(base_path, "data", "fixtures"),
    "combined": os.path.join(base_path, "data", "combined"),
    "collection": os.path.join(base_path, "data", "chroma", "docs"),
    "temp_files": os.path.join(base_path, "data", "sources_files", "_temp"),
    "temp_fixtures": os.path.join(base_path, "data", "fixtures", "_temp"),
    "temp_combined": os.path.join(base_path, "data", "combined", "_temp"),
    "temp_collection": os.path.join(base_path, "data", "chroma", "_temp"),
}

logging.basicConfig(
    filename=paths["logs"],  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


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


def process_file(file, process_type):
    """
    Process the file uploaded by the user
    
    Args:
    file: File uploaded by the user
    process_type: type of process ("temp" or "perm")
    
    Returns:
    result_validation: Validation result
    """
    file_path = os.path.join(paths["temp_files"], file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    if process_type == "temp":
        create_directories()
        result_storing = store_file(
            file_path,
            venv["mongo_user"],
            venv["mongo_pwd"],
            venv["mongo_host"],
            venv["mongo_port"],
            venv["mongo_db"],
        )

    result_download = download_files(
        venv["mongo_user"],
        venv["mongo_pwd"],
        venv["mongo_host"],
        venv["mongo_port"],
        venv["mongo_db"],
        process_type,
    )

    result_skills = get_skills(
        (
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            )
            if process_type == "temp"
            else os.path.join(
                paths["sources"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            )
        ),
        (
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx")
            if process_type == "temp"
            else os.path.join(paths["sources"], "Coaff_V1.xlsx")
        ),
        (
            os.path.join(paths["temp_files"], "descriptions_uniques.txt")
            if process_type == "temp"
            else os.path.join(paths["sources"], "profils_uniques.txt")
        ),
        (
            os.path.join(paths["temp_files"], "profils_uniques.txt")
            if process_type == "temp"
            else os.path.join(paths["sources"], "profils_uniques.txt")
        ),
    )

    result_fixtures = create_fixtures(
        (
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            )
            if process_type == "temp"
            else os.path.join(
                paths["sources"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            )
        ),
        (
            os.path.join(paths["temp_files"], "Coaff_V1.xlsx")
            if process_type == "temp"
            else os.path.join(paths["sources"], "Coaff_V1.xlsx")
        ),
        (
            os.path.join(
                paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
            )
            if process_type == "temp"
            else os.path.join(
                paths["sources"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
            )
        ),
        (
            os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_psarm.csv")
        ),
        (
            os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_coaff.csv")
        ),
        (
            os.path.join(paths["temp_fixtures"], "fixtures_certs.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_certs.csv")
        ),
    )

    response = requests.delete(
        f"http://{venv['db_api_host']}:{venv['db_api_port']}/profiles",
        json={"type": process_type},
    )
    response.raise_for_status()

    result_insert = insert_profiles(
        venv["db_api_host"],
        venv["db_api_port"],
        (
            os.path.join(paths["temp_fixtures"], "fixtures_psarm.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_psarm.csv")
        ),
        (
            os.path.join(paths["temp_fixtures"], "fixtures_coaff.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_coaff.csv")
        ),
        (
            os.path.join(paths["temp_fixtures"], "fixtures_certs.csv")
            if process_type == "temp"
            else os.path.join(paths["fixtures"], "fixtures_certs.csv")
        ),
        (
            os.path.join(paths["temp_combined"], "combined_result.csv")
            if process_type == "temp"
            else os.path.join(paths["combined"], "combined_result.csv")
        ),
        process_type,
    )

    result_embed = embed_documents(
        paths[f"temp_collection"] if process_type == "temp" else paths[f"collection"],
        process_type,
        MODEL_EMBEDDING,
    )

    test_embedding
    test_load_documents
    test_ollama

    result_validation = run_validation(
        paths[f"temp_collection"] if process_type == "temp" else paths[f"collection"],
        process_type,
        (
            os.path.join(paths["temp_combined"], "combined_result.csv")
            if process_type == "temp"
            else os.path.join(paths["combined"], "combined_result.csv")
        ),
        MODEL_EMBEDDING,
        GPT_4O_MINI,
    )

    if process_type == "temp":
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
            os.path.join(paths["sources"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"),
        )

    return result_validation


def delete_temp_files(file):

    if file.filename == "test_file.txt":
        os.remove(os.path.join(paths["temp_files"], "test_file.txt"))

    if os.path.exists(
        os.path.join(
            paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
        )
    ):
        os.remove(
            os.path.join(
                paths["temp_files"], "UC_RS_LP_RES_SKILLS_DETLS_22_1440892995.xlsx"
            )
        )
    if os.path.exists(os.path.join(paths["temp_files"], "Coaff_V1.xlsx")):
        os.remove(os.path.join(paths["temp_files"], "Coaff_V1.xlsx"))
    if os.path.exists(
        os.path.join(paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx")
    ):
        os.remove(
            os.path.join(
                paths["temp_files"], "UC_RS_RESOURCE_LIC_CERT_22_564150616.xlsx"
            )
        )
    if os.path.exists(os.path.join(paths["temp_files"], "descriptions_uniques.txt")):
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
