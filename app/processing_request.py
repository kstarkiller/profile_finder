import requests

ERROR_MESSAGES = {
    "no_data": "Please provide data to generate a response.",
    "no_question": "Please provide a question to answer.",
}

MODEL_LLM = "llama-3.1-70b-instruct"
MODEL_EMBEDDING = "nomic-embed-text:latest"


# This functions are used to process the user input and return the chatbot response via the generate_perplexity_response function.
def process_input(user_input, chat_history):
    """
    Process the user input and return the chatbot response and updated chat history.

    Args:
        user_input (str): The user input.
        chat_history (list): The chat history.

    Returns:
        str: The chatbot response.
        list: The updated chat history.
    """
    # Validation de l'entrée utilisateur
    if not user_input:
        return ERROR_MESSAGES["no_question"], chat_history

    # Ajouter l'entrée utilisateur à l'historique du chat
    chat_history.append({"role": "user", "content": user_input})

    # Récupérer les documents pertinents pour l'entrée utilisateur
    # documents = retrieve_documents(user_input, MODEL_EMBEDDING) or []

    # Générer une réponse via la fonction generate_perplexity_response
    # response = generate_perplexity_response(documents, chat_history, MODEL_LLM)

    # Générer une réponse via le point de terminaison de l'API RAG "/perplexity_chat"
    url = "http://localhost:8080/perplexity_chat"
    payload = {
        "question": user_input,
        "history": chat_history,
    }

    response = requests.post(url, json=payload)
    response_data = response.json()

    # Vérifier si la réponse contient des erreurs
    if response.status_code != 200:
        print(response_data)
        return (
            "Une erreur s'est produite lors de la génération de la réponse.",
            chat_history,
        )

    # Ajouter la réponse du chatbot à l'historique du chat
    chat_history.append(
        {"role": "assistant", "content": response_data.get("response", "")}
    )

    return response_data.get("response", ""), chat_history
