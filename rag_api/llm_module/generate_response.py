import os
import sys
import json
import ollama
import requests
from typing import Optional
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from log_module.custom_logging import log_response

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

# Path to the logs file
logs_path = os.path.join(
    os.path.dirname(__file__), "..", "log_module", "logs", "logs_api.log"
)

# Logging module configuration
logging.basicConfig(
    filename=logs_path,  # Log file name
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

session = requests.Session()


def validate_input(
    question: str,
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
    data: list, history: list, model: str = "llama3.1:8b"
) -> str:
    """
    Generates a response using the model of your choice (it must be downloaded locally).

    Args:
        data (list, optional): The data to use for the response.
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
        validate_input(question=history[-1]["content"], model=model)

        # Add the user and assistant messages to the prompt
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

        # Generate the response
        output = ollama.generate(
            model=model,
            prompt=json.dumps(prompt),
        )

        response = output["response"]
        log_response(
            history[-1]["content"], response
        )  # Log the asked question and the generated response
        return response

    except Exception as e:
        log_response(history[-1]["content"], str(e))  # Log the error message
        return str(e)


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
        #    "model": f"{model}"
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
def generate_minai_response(data: list, chat_id: str, history: list, model: str) -> str:
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
        validate_input(history[-1]["content"])

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
            "conversationId": f"{chat_id}",
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
        return f"I'm sorry, I can't answer you : {response.json()['message']}"

    except Exception as e:
        # Log the error message
        if not history or history == []:
            log_response("No history", str(e))
        else:
            log_response(history[-1]["content"], str(e))
        return "I'm sorry, I can't answer you :" + str(e)
