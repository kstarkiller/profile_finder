import os
import sys
import json
import getpass
import ollama
import requests
from requests.adapters import HTTPAdapter
import ssl
from typing import Optional
from datetime import date
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from log_module.custom_logging import log_access, log_response

# Import environment variables
USERNAME = os.getenv("RAG_LOCAL_USERNAME")
PASSWORD = os.getenv("RAG_LOCAL_PASSWORD")
MINAI_API_KEY = os.getenv("MINAI_API_KEY")

# Constants for error messages
ERROR_MESSAGES = {
    "access_denied": "Access denied. Invalid credentials.",
    "no_data": "Sorry, no data was provided. I need data to respond to your question. Please provide the data and try again.",
    "no_question": "I don't have a question to respond to. Please provide a valid question.",
    "question_too_long": "The question is too long. Please provide a question with less than 512 characters.",
    "invalid_model": "The model {} is not available. Please choose a valid model from this list: {}",
}

# Path to the collection
# sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
logs_path = os.path.join(
    os.path.dirname(__file__), "..", "log_module", "logs", "logs_api.log"
)

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)


# Personalized class to disable SSL verification
# class SSLAdapter(HTTPAdapter):
#     def init_poolmanager(self, *args, **kwargs):
#         context = ssl.create_default_context()
#         context.check_hostname = False
#         context.verify_mode = ssl.CERT_NONE
#         kwargs["ssl_context"] = context
#         return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)


# Global application of the custom SSL adapter to the requests session
session = requests.Session()
# adapter = SSLAdapter()
# session.mount("https://", adapter)


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

    # Authenticate the user if login information is provided
    if username and password:
        authenticated = authenticate(username, password)
        if not authenticated:
            logging.warning(ERROR_MESSAGES["access_denied"])
            raise ValueError(ERROR_MESSAGES["access_denied"])

    # Check if data is provided
    if not data:
        logging.warning(ERROR_MESSAGES["no_data"])
        raise ValueError(ERROR_MESSAGES["no_data"])

    # Check if data list is empty
    if not any(data):
        logging.warning(ERROR_MESSAGES["no_data"])
        raise ValueError(ERROR_MESSAGES["no_data"])

    # Check if the question is empty
    if not question or question.isspace() or not question.strip():
        logging.warning(ERROR_MESSAGES["no_question"])
        raise ValueError(ERROR_MESSAGES["no_question"])

    # Check if the question is too long
    if len(question) > 512:
        logging.warning(ERROR_MESSAGES["question_too_long"])
        raise ValueError(ERROR_MESSAGES["question_too_long"])

    # Check if the optional model argument is provided
    if model:
        # Check if the model is in the list of available models
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


# # Generate a conversation Title
# def generate_conversation_title(model: str, prompt: str) -> str:
#     url = "https://api.1min.ai/api/features?isStreaming=true"
#     headers = {
#         "API-KEY": f"{MINAI_API_KEY}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "type": "CHAT_WITH_AI",
#         "model": f"{model}",
#         "promptObject": {
#             "prompt": f"Résume le prompt suivant en quelques mots: {prompt}",
#             "isMixed": "false",
#             "webSearch": "false"
#         }
#     }

#     try:
#         conversation_title = session.post(url, headers=headers, json=payload)

#         return conversation_title

#     except requests.exceptions.HTTPError as e:
#         logging.error(f"HTTP error occurred: {str(e)}")
#         return "An unexpected error occurred" + str(e)
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request exception occurred 1: {str(e)}")
#         return "An unexpected error occurred" + str(e)
#     except ValueError as e:
#         logging.error(f"JSON decode error: {str(e)}")
#         return "Failed to decode JSON response: " + str(e)


def generate_conversation_id(model: str, prompt: str) -> str:
    # Set up the API request
    url = "https://api.1min.ai/api/conversations"
    headers = {
        "API-KEY": f"{MINAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Prepare the payload with the model
    payload = {
        "type": "CHAT_WITH_AI",
        "title": f"{prompt}",
        "model": f"{model}",
    }

    try:
        # Send the request to the Minai API
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Check if the response is empty
        if not response.text:
            logging.error("Empty response received from the API")
            return "Empty response received from the API"

        # Parse the response
        try:
            output = response.json()

        except ValueError as e:
            logging.error(f"JSON decode error: {str(e)}")
            return "An unexpected error occurred: JSON decode error"

        return output["conversation"]["uuid"]

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        return "An unexpected error occurred: " + str(e)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception occurred 2: {str(e)}")
        return "An unexpected error occurred: " + str(e)
    except ValueError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return "Failed to decode JSON response: " + str(e)


# Generate a response
def generate_minai_response(
    data: list, conversation_id: str, history: list, model: str
) -> str:
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
        if not history or history == []:
            logging.warning("History is empty")
            raise ValueError("History is empty")
        if not model:
            logging.warning("No model provided")
            raise ValueError("No model provided")
        # Validate inputs
        validate_input(data, history[-1]["content"])

        # Set up the API request
        url = "https://api.1min.ai/api/features?isStreaming=true"
        headers = {
            "API-KEY": f"{MINAI_API_KEY}",
            "Content-Type": "application/json",
        }

        # Add the user and assistant messages to the payload
        prompt = [
            {
                "role": history[0]["role"],
                "content": history[0]["content"]
                + "\n"
                + f"Use this data: {data} to respond to the user in this conversation.",
            }
        ]

        for i, message in enumerate(history[1:], start=1):
            prompt.append(
                {
                    "role": "user" if i % 2 == 1 else "assistant",
                    "content": message["content"],
                }
            )

        # Prepare the payload with the model
        payload = {
            "type": "CHAT_WITH_AI",
            "conversationId": f"{conversation_id}",
            "model": f"{model}",
            "promptObject": {
                "prompt": f"{prompt}",
                "isMixed": "false",
                "webSearch": "false",
            },
        }

        # Send the request to the Perplexity API
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad responses

        # Log HTTP response status if raised
        if response.status_code != 200:
            logging.error(f"1minAI API HTTP response status: {response.status_code}")
            print(response.status_code)
            logging.error(f"1minAI API HTTP response content: {response.content}")
            print(response.content)

        # # Parse the response
        # response_json = response.json()

        # Log and return the response
        log_response(history[-1]["content"], response.content)
        return response.content.decode("utf-8")

    except ValueError as e:
        # Log the error message
        if not history or history == []:
            log_response("No history", str(e))
        else:
            log_response(history[-1]["content"], str(e))
        return str(e)

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        return "An unexpected error occurred" + str(e)

    except Exception as e:
        # Log the error message
        if not history or history == []:
            log_response("No history", str(e))
        else:
            log_response(history[-1]["content"], str(e))
        return "An unexpected error occurred: " + str(e)