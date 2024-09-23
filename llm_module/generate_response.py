import os
import getpass
import ollama
import requests
from typing import Optional
from datetime import date
import logging

from log_module.custom_logging import log_access, log_response

# Import environment variables
USERNAME = os.getenv("RAG_LOCAL_USERNAME")
PASSWORD = os.getenv("RAG_LOCAL_PASSWORD")
API_KEY = os.getenv("RAG_LOCAL_API_KEY")

# Constants for error messages
ERROR_MESSAGES = {
    "access_denied": "Access denied. Invalid credentials.",
    "no_data": "Sorry, no data was provided. I need data to respond to your question. Please provide the data and try again.",
    "no_question": "I don't have a question to respond to. Please provide a valid question.",
    "question_too_long": "The question is too long. Please provide a question with less than 512 characters.",
    "invalid_model": "The model {} is not available. Please choose a valid model from this list: {}",
}

# Logs path according to the os
if os.name == "posix":
    logs_path = r"/home/kevin/simplon/briefs/avv-matcher/log_module/logs/local_api_access.log"
else:
    logs_path = r"C:\Users\k.simon\Projet\avv-matcher\log_module\logs\local_api_access.log"

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


# Authenticate the user
def authenticate(username: str, password: str) -> bool:
    """
    Authenticate the user using the credentials in the config file.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """

    # Check the credentials
    success = (username == USERNAME) and (password == PASSWORD)
    if success:
        log_access(username, success)  # Log the login attempt
        return success
    else:
        log_access(username, success)  # Log the login attempt
        return success


def validate_input(
    data: list,
    question: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    model: Optional[str] = None,
) -> None:
    """
    Valide les données d'entrée, la question et le modèle.

    Args:
        username (str): Le nom d'utilisateur de l'utilisateur.
        password (str): Le mot de passe de l'utilisateur.
        data (list): Les données à utiliser pour la réponse.
        question (str): La question à laquelle répondre.
        model (str): Le modèle à utiliser pour la réponse. Optionnel.

    Raises:
        ValueError: Si les données d'entrée, la question ou le modèle sont invalides.
    """

    # Authentifier l'utilisateur si les informations de connexion sont fournies
    if username and password:
        authenticated = authenticate(username, password)
        if not authenticated:
            logging.warning(ERROR_MESSAGES["access_denied"])
            raise ValueError(ERROR_MESSAGES["access_denied"])

    # Vérifier si les données sont fournies
    if not data:
        logging.warning(ERROR_MESSAGES["no_data"])
        raise ValueError(ERROR_MESSAGES["no_data"])
    
    # Vérifier si la liste de données est vide
    if not any(data):
        logging.warning(ERROR_MESSAGES["no_data"])
        raise ValueError(ERROR_MESSAGES["no_data"])

    # Vérifier si la question est vide
    if not question or question.isspace() or not question.strip():
        logging.warning(ERROR_MESSAGES["no_question"])
        raise ValueError(ERROR_MESSAGES["no_question"])

    # Vérifier si la question est trop longue
    if len(question) > 512:
        logging.warning(ERROR_MESSAGES["question_too_long"])
        raise ValueError(ERROR_MESSAGES["question_too_long"])

    # Vérifier si l'argument optionnel model est fourni
    if model:
        # Vérifier si le modèle est dans la liste des modèles disponibles
        available_models = ollama.list().get("models", [])
        model_names = [m["name"] for m in available_models]
        if model not in model_names:
            logging.warning(ERROR_MESSAGES["invalid_model"].format(model, model_names))
            raise ValueError(ERROR_MESSAGES["invalid_model"].format(model, model_names))


def generate_ollama_response(
    data: list, question: str, model: str = "llama3.1:8b"
) -> str:
    """
    Generates a response using the model of your choice (llama3.1 8B here).

    Args:
        data (list): The data to use for the response.
        question (str): The question to respond to.
        model (str): The model to use for the response.

    Returns:
        str: The generated response.
    """

    # Let user enter their credentials
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        # Validate inputs
        validate_input(data, question, username, password, model)

        prompt = f"""
            You are a French chatbot assistant that helps the user find team members based on their location, availability and skills.
            - Format responses as concise and consistently as possible, using headers and tables when necessary. Don't explain what you're doing and summarize the data.
            - Use the current date ({date.today()}) for any time-related questions.
            - For months, consider the nearest future month unless otherwise specified. Don't consider months in the past or months more than 12 months in the futur, unless otherwise specified.
            - Combine occupancy periods and percentages to calculate total availability over a given period.
            - Don't assume anything, don't mess with the data, and only return members that meet the user's criteria.
            - If several members match the criteria, present them in order of relevance (availability, skills, etc.).
            Using this data: {data}, respond to this prompt: {question}.
            """

        # Generate the response
        output = ollama.generate(
            model=model,
            prompt=prompt,
        )

        response = output["response"]
        log_response(
            question, response
        )  # Log the asked question and the generated response
        return response

    except Exception as e:
        log_response(question, str(e))  # Log the error message
        return str(e)


# Generate a response
def generate_perplexity_response(data: list, history: list, model: str) -> str:
    """
    Generates a response using the Perplexity API.

    Args:
        data (list): The data to use for the response.
        history (list): The chat history.
        model (str): The model to use for the response.

    Returns:
        str: The generated response.
    """

    try:
        if not history or history==[]:
            logging.warning("History is empty")
            raise ValueError("History is empty")
        if not model:
            logging.warning("No model provided")
            raise ValueError("No model provided")
        # Validate inputs
        validate_input(data, history[-1]["content"])

        # Set up the API request
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        # Prepare the payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": history[0]["role"],
                    "content": history[0]["content"]
                    + "\n"
                    + f"Use this data: {data} to respond to the user in this conversation.",
                }
            ],
        }

        # Add the user and assistant messages to the payload
        for i, message in enumerate(history[1:], start=1):
            payload["messages"].append(
                {
                    "role": "user" if i % 2 == 1 else "assistant",
                    "content": message["content"],
                }
            )

        # Send the request to the Perplexity API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        # log HTTP response status if raised
        if response.status_code != 200:
            logging.error(f"Perplexity API HTTP response status: {response.status_code}")
            print(response.status_code)
            logging.error(f"Perplexity API HTTP response content: {response.content}")
            print(response.content)

        # Parse the response
        output = response.json()
        generated_response = output["choices"][0]["message"]["content"]

        # Log and return the response
        log_response(history[-1]["content"], generated_response)
        return generated_response

    except ValueError as e:
        # Log the error message
        if not history or history == []:
            log_response("No history", str(e))
        else:
            log_response(history[-1]["content"], str(e))
        return str(e)

    except Exception as e:
        # Log the error message
        if not history or history == []:
            log_response("No history", str(e))
        else:
            log_response(history[-1]["content"], str(e))
        return "An unexpected error occurred: " + str(e)
