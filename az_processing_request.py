import os
from openai import AzureOpenAI
from az_search import find_profiles_azure

LLM_gpt4 = "aiprofilesmatching-gpt4"
LLM_gpt4_turbo = "gpt-4-turbo-1106-preview"
EMBEDDER = "aiprofilesmatching-text-embedding-3-large"

# Initialiser le client AzureOpenAI
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),  # type: ignore
)


def process_input(user_input, chat_history):
    """
    Process the user input and return the chatbot response.

    :param user_input: list of dict containing the user input and context (if any) as a string (e.g. [{"query": "Hello, how are you?", "context": ""}])
    :param chat_history: list of dict containing the chat history (user and assistant messages) as strings
    :return: str, list of dict
    """
    # Validation de l'entrée utilisateur
    if not user_input[-1]["query"].strip():
        return "Please enter a valid input.", chat_history

    # Vérifier que chat_history ne contient que le contexte de départ (system)
    # Il s'agit donc de la première requête de l'utilisateur
    if len(chat_history) <= 1:
        # Vérifier que le context n'est pas vide ou null
        if user_input[-1]["context"] != "":
            # Prétraitement de l'entrée utilisateur
            profiles = find_profiles_azure(user_input, EMBEDDER)

            # Verifier si la liste des profils n'est pas vide
            if (
                len(profiles) != 0
                or profiles[0] != "Input too long. Please enter a shorter input."
            ):
                # Convertir les profils en string
                profiles = [str(profile) for profile in profiles]

                chat_history.append(
                    {
                        "role": "system",
                        "content": "Use the following profiles in this conversation: "
                        + ", ".join(profiles),
                    }
                )

    prompt = user_input[-1]["query"]

    # Ajouter la nouvelle entrée utilisateur à l'historique
    chat_history.append({"role": "user", "content": prompt})

    # Créer une requête de complétion de chat en utilisant le client Azure OpenAI
    try:
        completion = client.chat.completions.create(
            model=LLM_gpt4_turbo, messages=chat_history
        )

        # Récupérer la réponse du modèle
        if hasattr(completion, "choices") and len(completion.choices) > 0:
            first_choice = completion.choices[0]
            if hasattr(first_choice, "message") and hasattr(
                first_choice.message, "content"
            ):
                response = first_choice.message.content
                # Ajouter la réponse du chatbot à l'historique
                chat_history.append({"role": "assistant", "content": response})

                return response, chat_history
            else:
                raise AttributeError("First choice message has no 'content' attribute")
        else:
            raise AttributeError(
                "'choices' attribute missing or empty in completion object"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing the input.", chat_history
