import pandas as pd
from datetime import date

from rag_module.embedding import retrieve_documents
from llm_module.generate_response import generate_ollama_response


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


def validate_response(combined_path: str, question: str, llm_response: str) -> tuple:
    """
    Validates the response.

    Args:
        combined_path (str): The path to the CSV file.
        question (str): The question.
        llm_response (str): The response.

    Returns:
        tuple: The validation result and message.
    """
    data = import_data(combined_path)

    if "compétence" in question:
        expected_names = [
            membre["Nom"] for membre in data if "Python" in membre["Combined"]
        ]
    elif "certification" in question:
        expected_names = [
            membre["Nom"] for membre in data if "Certificat A" in membre["Combined"]
        ]
    else:
        expected_names = []

    # Vérification si les noms attendus sont présents dans la réponse
    if expected_names:
        for name in expected_names:
            if name not in llm_response:
                return False, f"Erreur : '{name}' n'est pas mentionné dans la réponse."
        return True, "Réponse valide."
    return False, "Aucune vérification nécessaire."


def run_validation(
    collection: str, combined_path: str, embed_model: str, llm_model: str
) -> str:
    """
    Runs the validation process.

    Args:
        data_path (str): The path to the CSV file.
        model_path (str): The path to the model.

    Returns:
        str: The validation result.
    """
    questions = [
        "Liste les membres ayant la compétence 'Python'.",
        "Quels membres ont obtenu la certification 'Scrum' ?",
    ]

    results = {}

    for i, question in enumerate(questions):
        history = [
            {
                "role": "system",
                "content": "You are a French chatbot assistant that helps the user find team members",
            },
            {"role": "user", "content": question},
        ]
        data = retrieve_documents(collection, question, embed_model)
        llm_response = generate_ollama_response(data, history, llm_model)

        # Validation de la réponse
        valid, message = validate_response(combined_path, question, llm_response)
        results[f"Question {i+1}"] = {
            "question": question,
            "response": llm_response,
            "valid": valid,
            "info": message,
        }

    count_false = sum([1 for result in results.values() if not result["valid"]])
    false_rate = (count_false / len(results)) * 100

    return results, false_rate
