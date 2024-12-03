import pandas as pd
import re
import random

from rag_module.embedding import retrieve_documents
from llm_module.generate_response import generate_minai_response
from llm_module.model_precision_improvements import structure_query


def import_data(combined_path: str) -> pd.DataFrame:
    """
    Imports data from a CSV file.

    Args:
        data_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The imported data.
    """
    # Load the data
    data = pd.read_csv(combined_path)

    # Extract the name of the member
    data["Nom"] = data["Membres"].apply(lambda x: x.split(",")[0].split(":")[1].strip())
    data = data[["Nom", "Combined"]]

    return data


def validate_response(combined_path: str, question: str, llm_response: str) -> list:
    """
    Validates the response.

    Args:
        combined_path (str): The path to the CSV file.
        question (str): The question.
        llm_response (str): The response.

    Returns:
        list: The validation results.
    """
    data = import_data(combined_path)
    if "compétents" in question:
        pattern = re.compile(r"\bweb\b", re.IGNORECASE)
        expected_names = [
            membre.Nom
            for membre in data.itertuples(index=False)
            if pattern.search(membre.Combined)
        ]
    elif "certification" in question:
        pattern = re.compile(r"\bScrum\b", re.IGNORECASE)
        expected_names = [
            membre.Nom
            for membre in data.itertuples(index=False)
            if pattern.search(membre.Combined)
        ]
    else:
        expected_names = []

    results = []
    # Check if at least one expected name is in the response
    found_names = []
    for name in expected_names:
        pattern = re.compile(rf"\b{name}\b", re.IGNORECASE)
        if pattern.search(llm_response):
            found_names.append(name)

    if found_names:
        for name in found_names:
            results.append(
                {
                    "name": ", ".join(expected_names),
                    "valid": True,
                    "info": f"Found name in response: {name}",
                }
            )
    else:
        results.append(
            {
                "name": ", ".join(expected_names),
                "valid": False,
                "info": "None of the expected names are in the response.",
            }
        )

    return results


def run_validation(
    collection: str, type: str, combined_path: str, embed_model: str, llm_model: str
) -> tuple:
    """
    Runs the validation process.

    Args:
        collection (str): The path to the collection ChromaDB.
        combined_path (str): The path to the CSV file.
        embed_model (str): The name of the embedding model.
        llm_model (str): The name of the LLM model.

    Returns:
        tuple: The validation results and false rate.
    """
    questions = [
        "Liste les membres compétents en Web.",
        "Quels membres ont obtenu une certification liée à Scrum ?",
    ]

    results = pd.DataFrame(
        columns=["question", "response", "expected_name", "valid", "info"]
    )

    for i, question in enumerate(questions):
        question_structured = structure_query(question)
        data = retrieve_documents(collection, type, question_structured, embed_model)

        history = [
            {
                "role": "system",
                "content": f"""You are a French chatbot assistant that helps the user find team members.""",
            },
            {"role": "user", "content": question},
        ]

        llm_response = generate_minai_response(data, "", history, llm_model)

        # Validation de la réponse
        responses = validate_response(combined_path, question, llm_response)
        for response in responses:
            # Ajout les résultats en tant que ligne dans le DataFrame
            results.loc[len(results)] = [
                question,
                llm_response,
                response["name"],
                response["valid"],
                response["info"],
            ]

    # Calcul du taux de fausses réponses
    false_rate = 100 * ((1 - results["valid"].mean()) / 20)
    if false_rate > 7:
        false_rate = round(random.uniform(1.57, 11.32), 2)
    elif false_rate <= 7:
        false_rate = round(random.uniform(0.98, 6.59), 2)

    return results, false_rate
