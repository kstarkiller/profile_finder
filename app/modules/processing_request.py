import requests
import json

from modules.docker_check import is_running_in_docker

ERROR_MESSAGES = {
    "no_data": "Please provide data to generate a response.",
    "no_question": "Please provide a question to answer.",
}

venv = is_running_in_docker()


# These functions are used to process the user input and return the chatbot response via the generate_perplexity_response function.
def process_input(user_input, chat_history, chat_id, model, token):
    """
    Process the user input and return the chatbot response and updated chat history.

    Args:
        user_input (str): The user input.
        chat_history (list): The chat history.
        chat_id (str): The chat ID.

    Returns:
        str: The chatbot response.
        list: The updated chat history.
        float: The duration of the response generation.
    """
    # Validate user input
    if not user_input:
        return ERROR_MESSAGES["no_question"], chat_history

    # Add user input to chat history
    chat_history.append({"role": "user", "content": user_input})

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Determine the URL based on the model
    url = f"http://{venv['rag_host']}:{venv['rag_port']}/chat"

    try:
        if model in ["llama3.1:8b", "gemma2:9b", "phi3.5:3.8b"]:
            service_type = "ollama"
        else:
            service_type = "minai"
        # Generate a response via the RAG API endpoint
        payload = {
            "service_type": service_type,
            "question": user_input,
            "history": chat_history,
            "chat_id": chat_id,
            "model": model,
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        # Check if the response contains errors
        if response.status_code != 200:
            return (
                "An error occurred while generating the response.",
                chat_history,
            )

        # Add chatbot response to chat history
        chat_history.append(
            {"role": "assistant", "content": response_data.get("response", "")}
        )

        return (
            response_data.get("response", ""),
            chat_history,
            response_data.get("duration", 0),
        )
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}", chat_history
