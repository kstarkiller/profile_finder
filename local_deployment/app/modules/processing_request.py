import requests
import json

ERROR_MESSAGES = {
    "no_data": "Please provide data to generate a response.",
    "no_question": "Please provide a question to answer.",
}

MODEL_LLM = "llama-3.1-70b-instruct"
MODEL_EMBEDDING = "nomic-embed-text:latest"


# These functions are used to process the user input and return the chatbot response via the generate_perplexity_response function.
def process_input(user_input, chat_history, chat_id):
    """
    Process the user input and return the chatbot response and updated chat history.

    Args:
        user_input (str): The user input.
        chat_history (list): The chat history.

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

    # Generate a response via the RAG API endpoint "/minai_chat"
    url = "http://localhost:8080/minai_chat"
    payload = {
        "question": user_input,
        "history": chat_history,
        "chat_id": chat_id,
    }

    response = requests.post(url, json=payload)
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
